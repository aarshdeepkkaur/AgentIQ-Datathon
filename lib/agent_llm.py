
"""LLM-powered AgentIQ using Groq.

The agent:
1. Sends the user's question + dataframe schema to Groq.
2. Groq generates a pandas query.
3. The query runs locally against the already-loaded cleaned DataFrames.
4. The result is sent back to Groq for a concise explanation.
5. The explanation can be streamed back to the frontend.

No Emergent integration is required.
"""

import asyncio
import json
import logging
import os
import re
from collections.abc import AsyncIterator
from typing import Any

import numpy as np
import pandas as pd

from lib.analytics import filter_bundle, num
from lib.datasets import CROPS, DatasetBundle
from models.agent import AgentChartPoint

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Groq configuration
# ---------------------------------------------------------------------------

MODEL_PROVIDER = "groq"

# Can be overridden with GROQ_MODEL in .env
MODEL_NAME = os.environ.get(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)

EXEC_TIMEOUT_SECONDS = 25


# ---------------------------------------------------------------------------
# Safety restrictions for generated pandas code
# ---------------------------------------------------------------------------

FORBIDDEN = re.compile(
    r"("
    r"__"
    r"|\bimport\s+(?!pandas|numpy)\w+"
    r"|\bopen\s*\("
    r"|\beval\s*\("
    r"|\bexec\s*\("
    r"|\bos\."
    r"|\bsys\."
    r"|subprocess"
    r"|shutil"
    r"|socket"
    r"|pathlib"
    r"|to_csv"
    r"|to_pickle"
    r"|to_excel"
    r"|read_csv"
    r"|read_pickle"
    r"|\bglobals\s*\("
    r"|\blocals\s*\("
    r"|getattr"
    r"|setattr"
    r"|\binput\s*\("
    r")"
)


# ---------------------------------------------------------------------------
# Data schema given to the LLM
# ---------------------------------------------------------------------------

SCHEMA_DOC = f"""
You answer questions about an Indian agricultural mandi supply chain.

FIVE pandas DataFrames are ALREADY LOADED in scope.
Do not load files and do not access the network.

master (57 rows, one per mandi):
- mandi_id (str, e.g. "MANDI001")
- mandi_name (str)
- district (str, may be NaN)
- state (str: Punjab / Haryana / Uttar Pradesh, may be NaN)
- mandi_type (str)
- total_area_acres (float)

arrivals:
- arrival_id
- date (datetime64)
- mandi_id
- crop_name (str, canonical)
- variety
- arrival_quantity_qtl (float, around 42% NaN)
- farmer_count (float)
- quality_flag (str or NaN)

IMPORTANT:
arrival_quantity_qtl may contain NaN.
Always drop NaN before summing or averaging quantities.

prices:
- record_id
- date (datetime64)
- mandi_id
- district
- crop_name (str, canonical)
- min_price
- max_price
- modal_price (float, ₹/quintal, some NaN)
- msp (float, ₹/quintal, some NaN)

"Below MSP" means:
modal_price < msp
only on rows where both values are present.

transport:
- trip_id
- mandi_id
- destination_warehouse
- departure_time_clean
- arrival_time_clean
- transit_hours (float, some NaN)
- distance_km
- vehicle_no_clean
- driver_id
- quality_flag

A trip is delayed when:
transit_hours > 24

weather:
- sensor_id
- timestamp_ist
- temperature_c
- rainfall_mm
- humidity_percent

Weather is NOT directly linked to mandis.

Canonical crop names:
{", ".join(CROPS)}

Join mandi names using:
master.mandi_id == other_dataframe.mandi_id

Dates run Jan-Dec 2026.

Currency:
₹ per quintal (qtl).
"""


# ---------------------------------------------------------------------------
# Code-generation system prompt
# ---------------------------------------------------------------------------

CODE_SYSTEM = SCHEMA_DOC + """

You are the data-analysis engine for AgentIQ.

Write ONE self-contained pandas snippet that answers the user's question.

Rules:

1. Only use pandas (pd) and numpy (np).
2. They are already imported.
3. Do not import anything else.
4. Do not load files.
5. Do not access the network.
6. Do not access the operating system.
7. Do not use open(), eval(), exec(), os, sys, subprocess, sockets, pathlib, etc.
8. Assign the final answer to a variable named `result`.
9. `result` must be either:
   - a pandas DataFrame, preferably <= 30 rows
   - a pandas Series
   - or a scalar
10. Prefer readable DataFrame columns.
11. Reset indexes where appropriate.
12. Prefer grouping by mandi_name after merging with master.
13. Round numerical values where appropriate.
14. If the question asks for a comparison, return the relevant rows rather than only one unexplained number.
15. If the result is suitable for a bar chart, provide chart metadata.

The selected dashboard crop will be supplied with the user question.
If the user says "this crop" or does not specify a crop, use that selected crop.

Return ONLY valid JSON.

Expected format:

{
  "approach": "one sentence describing the analysis",
  "code": "python code",
  "chart": {
    "label_col": "column name",
    "value_col": "column name",
    "unit": "₹ | qtl | h | % | mm | °C | rows"
  }
}

If no chart is appropriate:

{
  "approach": "one sentence",
  "code": "python code",
  "chart": null
}
"""


# ---------------------------------------------------------------------------
# Explanation system prompt
# ---------------------------------------------------------------------------

EXPLAIN_SYSTEM = SCHEMA_DOC + """

You are AgentIQ, a concise agricultural supply-chain analyst.

The pandas code has already been executed successfully.

Given:
- the user's question
- the executed pandas code
- the resulting data

Write the final answer for a dashboard chat panel.

Rules:
- 2-4 sentences.
- Plain text.
- No markdown headers.
- No code.
- Cite concrete numbers from the supplied result.
- Use ₹ with thousands separators for prices.
- Use qtl for quantities.
- Use h for hours.
- Mention caveats only when the result is empty or clearly limited.
- Never invent numbers.
- Do not claim anything that is not supported by the result.
"""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LlmUnavailable(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------------

def llm_enabled() -> bool:
    """Return True when a Groq API key is configured."""
    return bool(os.environ.get("GROQ_API_KEY"))


def _get_client():
    """Create an async Groq client."""
    try:
        from groq import AsyncGroq
    except ImportError as exc:
        raise LlmUnavailable(
            "Groq SDK is not installed. Run: pip install groq"
        ) from exc

    key = os.environ.get("GROQ_API_KEY")

    if not key:
        raise LlmUnavailable(
            "GROQ_API_KEY is not configured"
        )

    return AsyncGroq(api_key=key)


async def _chat(
    system_message: str,
    user_message: str,
) -> str:
    """Send a normal non-streaming request to Groq."""

    client = _get_client()

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0,
        max_tokens=4096,
        stream=False,
    )

    content = response.choices[0].message.content

    if not content:
        raise LlmUnavailable("Groq returned an empty response")

    return content


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------

def _parse_json(raw: str) -> dict[str, Any]:
    """Parse JSON even if the model accidentally adds markdown fences."""

    cleaned = raw.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "Groq did not return a JSON object"
        )

    parsed = json.loads(
        cleaned[start : end + 1]
    )

    if not isinstance(parsed, dict):
        raise ValueError(
            "Groq returned JSON but not an object"
        )

    return parsed


# ---------------------------------------------------------------------------
# Generate pandas code
# ---------------------------------------------------------------------------

async def generate_code(
    question: str,
    crop: str,
    session_id: str,
    previous_error: str | None = None,
    previous_code: str | None = None,
) -> dict[str, Any]:

    prompt = (
        f"Selected crop in the dashboard: {crop}\n\n"
        f"User question:\n{question}"
    )

    if previous_error:
        prompt += (
            "\n\nYour previous pandas code failed."
            "\nFix the code and return a corrected JSON object."
            f"\n\nPrevious code:\n{previous_code}"
            f"\n\nError:\n{previous_error}"
        )

    raw = await _chat(
        CODE_SYSTEM,
        prompt,
    )

    plan = _parse_json(raw)

    if not isinstance(plan.get("code"), str):
        raise ValueError(
            "Groq returned no pandas code"
        )

    if not plan["code"].strip():
        raise ValueError(
            "Groq returned empty pandas code"
        )

    return plan


# ---------------------------------------------------------------------------
# Restricted Python builtins
# ---------------------------------------------------------------------------

def _safe_builtins() -> dict[str, Any]:
    import builtins

    allowed = (
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "float",
        "int",
        "len",
        "list",
        "max",
        "min",
        "range",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
        "isinstance",
        "print",
        "map",
        "filter",
        "reversed",
        "True",
        "False",
        "None",
    )

    return {
        name: getattr(builtins, name)
        for name in allowed
        if hasattr(builtins, name)
    }


# ---------------------------------------------------------------------------
# Execute generated pandas code
# ---------------------------------------------------------------------------

def _execute(
    code: str,
    bundle: DatasetBundle,
) -> Any:

    # Remove harmless pandas/numpy import statements.
    # pd and np are already supplied in the namespace.
    code = "\n".join(
        line
        for line in code.splitlines()
        if not re.match(
            r"^\s*import\s+(pandas|numpy)"
            r"(\s+as\s+\w+)?\s*$",
            line,
        )
    )

    if FORBIDDEN.search(code):
        raise ValueError(
            "Code uses a disallowed operation. "
            "Only pandas/numpy analysis over the loaded "
            "dataframes is permitted."
        )

    namespace: dict[str, Any] = {
        "__builtins__": _safe_builtins(),

        "pd": pd,
        "np": np,

        "master": bundle.master.copy(),
        "arrivals": bundle.arrivals.copy(),
        "prices": bundle.prices.copy(),
        "transport": bundle.transport.copy(),
        "weather": bundle.weather.copy(),
    }

    exec(
        compile(
            code,
            "<agentiq>",
            "exec",
        ),
        namespace,
    )

    if "result" not in namespace:
        raise ValueError(
            "Generated code did not assign `result`"
        )

    return namespace["result"]


async def run_code(
    code: str,
    bundle: DatasetBundle,
) -> Any:

    return await asyncio.wait_for(
        asyncio.to_thread(
            _execute,
            code,
            bundle,
        ),
        timeout=EXEC_TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------------
# Result preview
# ---------------------------------------------------------------------------

def preview(
    result: Any,
    limit: int = 30,
) -> tuple[str, int]:

    if isinstance(result, pd.DataFrame):

        frame = result.head(limit)

        return (
            frame.to_string(
                index=False,
                max_colwidth=32,
            ),
            int(len(result)),
        )

    if isinstance(result, pd.Series):

        frame = (
            result
            .head(limit)
            .to_frame(
                name=result.name or "value"
            )
            .reset_index()
        )

        return (
            frame.to_string(
                index=False,
                max_colwidth=32,
            ),
            int(len(result)),
        )

    return str(result), 1


# ---------------------------------------------------------------------------
# Chart conversion
# ---------------------------------------------------------------------------

def chart_points(
    result: Any,
    spec: dict[str, Any] | None,
) -> list[AgentChartPoint]:

    if (
        not spec
        or not isinstance(result, pd.DataFrame)
        or result.empty
    ):
        return []

    label_col = spec.get("label_col")
    value_col = spec.get("value_col")

    if (
        label_col not in result.columns
        or value_col not in result.columns
    ):
        return []

    unit = str(
        spec.get("unit") or ""
    )

    points: list[AgentChartPoint] = []

    for _, row in result.head(8).iterrows():

        try:
            value = float(
                row[value_col]
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        if np.isnan(value):
            continue

        points.append(
            AgentChartPoint(
                label=str(
                    row[label_col]
                )[:24],
                value=num(value),
                unit=unit,
            )
        )

    return points


# ---------------------------------------------------------------------------
# Streaming explanation
# ---------------------------------------------------------------------------

async def stream_explanation(
    question: str,
    code: str,
    result_text: str,
    rows: int,
    session_id: str,
) -> AsyncIterator[str]:

    client = _get_client()

    prompt = (
        f"Question:\n{question}\n\n"
        f"Code that ran:\n{code}\n\n"
        f"Result ({rows} row(s), first 30 shown):\n"
        f"{result_text}"
    )

    stream = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": EXPLAIN_SYSTEM,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=1000,
        stream=True,
    )

    async for chunk in stream:

        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        if delta.content:
            yield delta.content


# ---------------------------------------------------------------------------
# Main AgentIQ pipeline
# ---------------------------------------------------------------------------

async def plan_and_execute(
    question: str,
    crop: str,
    session_id: str,
    full_bundle: DatasetBundle,
    date_from: str | None,
    date_to: str | None,
) -> tuple[dict[str, Any], Any]:
    """
    Main AgentIQ workflow.

    1. Filter dashboard data by date.
    2. Ask Groq to generate pandas code.
    3. Execute the generated code locally.
    4. If execution fails, send the error back to Groq once.
    5. Return the generated plan and result.
    """

    bundle = filter_bundle(
        full_bundle,
        date_from,
        date_to,
    )

    plan = await generate_code(
        question,
        crop,
        session_id,
    )

    try:

        result = await run_code(
            plan["code"],
            bundle,
        )

    except (
        Exception,
        asyncio.TimeoutError,
    ) as exc:

        logger.info(
            "AgentIQ generated code failed. "
            "Retrying with Groq: %s",
            exc,
        )

        plan = await generate_code(
            question,
            crop,
            session_id,
            previous_error=(
                f"{type(exc).__name__}: {exc}"
            ),
            previous_code=plan["code"],
        )

        result = await run_code(
            plan["code"],
            bundle,
        )

    return plan, result


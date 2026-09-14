"""LLM-powered AgentIQ: Claude writes a pandas query over the cleaned DataFrames, we execute it in a
restricted namespace, then Claude explains the result. Falls back to rule-based answers on any failure."""

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

MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-sonnet-4-5-20250929"
EXEC_TIMEOUT_SECONDS = 25
FORBIDDEN = re.compile(r"(__|\bimport\s+(?!pandas|numpy)\w+|\bopen\s*\(|\beval\s*\(|\bexec\s*\(|\bos\.|\bsys\.|subprocess|shutil|socket|pathlib|to_csv|to_pickle|to_excel|read_csv|read_pickle|\bglobals\s*\(|\blocals\s*\(|getattr|setattr|\binput\s*\()")

SCHEMA_DOC = f"""You answer questions about an Indian agricultural mandi supply chain using FIVE pandas DataFrames that are ALREADY LOADED in scope (do not load files):

master (57 rows, one per mandi): mandi_id (str e.g. "MANDI001"), mandi_name (str), district (str, may be NaN), state (str: Punjab / Haryana / Uttar Pradesh, may be NaN), mandi_type (str), total_area_acres (float)
arrivals (mandi arrivals): arrival_id, date (datetime64), mandi_id, crop_name (str, canonical), variety, arrival_quantity_qtl (float quintals, ~42% NaN — always dropna before summing/averaging), farmer_count (float), quality_flag (str or NaN)
prices (price & MSP): record_id, date (datetime64), mandi_id, district, crop_name (str, canonical), min_price, max_price, modal_price (float ₹/quintal, some NaN), msp (float ₹/quintal, ~20% NaN). "Below MSP" means modal_price < msp on rows where both are present.
transport (trips): trip_id, mandi_id, destination_warehouse (str: WH-NORTH, WH-SOUTH, WH-EAST, WH-WEST, WH-CENTRAL, EXPORT-TERMINAL), departure_time_clean (str "YYYY-MM-DD HH:MM:SS"), arrival_time_clean (str), transit_hours (float, some NaN), distance_km (float), vehicle_no_clean, driver_id, quality_flag (str or NaN). A trip is "delayed" when transit_hours > 24.
weather (sensor rows, NOT linked to mandis): sensor_id, timestamp_ist (tz-aware datetime64, UTC-stored; use .dt.tz_convert("Asia/Kolkata")), temperature_c (float, some NaN), rainfall_mm (float, some NaN), humidity_percent (float, some NaN)

Canonical crop names in crop_name: {", ".join(CROPS)}. Join mandi names via master on mandi_id. Dates run Jan–Dec 2026. Currency is ₹ per quintal (qtl)."""

CODE_SYSTEM = SCHEMA_DOC + """

Write ONE self-contained pandas snippet that answers the user's question. Rules:
- Use only pandas (pd) and numpy (np); they are already imported. No file, network, or OS access. No other imports.
- Assign the final answer to a variable named `result`: a DataFrame (preferred, ≤ 30 rows, human-readable column names, rounded numbers) or a scalar.
- Reset the index so key columns (e.g. mandi_id, mandi_name, crop_name, destination_warehouse, month) are real columns.
- Prefer grouping by mandi_name (merged from master) so results are readable.
- If the result is suitable for a bar chart, name the label column and numeric column.
Respond with ONLY a JSON object, no markdown fences: {"approach": "<one sentence>", "code": "<python code>", "chart": {"label_col": "<col>", "value_col": "<col>", "unit": "<₹ | qtl | h | % | mm | °C | rows>"} or null}"""

EXPLAIN_SYSTEM = SCHEMA_DOC + """

You are AgentIQ, a concise supply-chain analyst. Given the user's question, the pandas code that ran, and its result, write the answer for a dashboard chat panel:
- 2–4 sentences, plain text, no markdown headers or code. Cite concrete numbers from the result (₹ with thousands separators, quintals as qtl, hours as h).
- Mention caveats only if the result is empty or clearly limited.
- Never invent numbers that are not in the result."""


class LlmUnavailable(RuntimeError):
    pass


def llm_enabled() -> bool:
    return bool(os.environ.get("EMERGENT_LLM_KEY"))


def _chat(system_message: str, session_id: str):
    from emergentintegrations.llm.chat import LlmChat

    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise LlmUnavailable("EMERGENT_LLM_KEY is not configured")
    return LlmChat(api_key=key, session_id=session_id, system_message=system_message).with_model(MODEL_PROVIDER, MODEL_NAME)


def _parse_json(raw: str) -> dict[str, Any]:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("model did not return JSON")
    return json.loads(cleaned[start : end + 1])


async def generate_code(question: str, crop: str, session_id: str, previous_error: str | None = None, previous_code: str | None = None) -> dict[str, Any]:
    from emergentintegrations.llm.chat import UserMessage

    prompt = f"Selected crop in the dashboard: {crop} (use it when the question says 'this crop' or names no crop).\nQuestion: {question}"
    if previous_error:
        prompt += f"\n\nYour previous code failed. Fix it.\nPrevious code:\n{previous_code}\nError: {previous_error}"
    chat = _chat(CODE_SYSTEM, f"{session_id}-code")
    raw = await chat.send_message(UserMessage(text=prompt))
    plan = _parse_json(str(raw))
    if not isinstance(plan.get("code"), str) or not plan["code"].strip():
        raise ValueError("model returned no code")
    return plan


def _safe_builtins() -> dict[str, Any]:
    import builtins

    allowed = ("abs", "all", "any", "bool", "dict", "enumerate", "float", "int", "len", "list", "max", "min", "range", "round", "set", "sorted", "str", "sum", "tuple", "zip", "isinstance", "print", "map", "filter", "reversed", "True", "False", "None")
    return {name: getattr(builtins, name) for name in allowed if hasattr(builtins, name)}


def _execute(code: str, bundle: DatasetBundle) -> Any:
    # pandas/numpy are pre-bound; drop redundant import lines so the sandbox never needs __import__.
    code = "\n".join(line for line in code.splitlines() if not re.match(r"^\s*import\s+(pandas|numpy)(\s+as\s+\w+)?\s*$", line))
    if FORBIDDEN.search(code):
        raise ValueError("code uses a disallowed operation (only pandas/numpy analysis over the loaded frames is permitted)")
    namespace: dict[str, Any] = {
        "__builtins__": _safe_builtins(), "pd": pd, "np": np,
        "master": bundle.master.copy(), "arrivals": bundle.arrivals.copy(), "prices": bundle.prices.copy(),
        "transport": bundle.transport.copy(), "weather": bundle.weather.copy(),
    }
    exec(compile(code, "<agentiq>", "exec"), namespace)  # noqa: S102 - restricted namespace, analysis-only demo agent
    if "result" not in namespace:
        raise ValueError("code did not assign `result`")
    return namespace["result"]


async def run_code(code: str, bundle: DatasetBundle) -> Any:
    return await asyncio.wait_for(asyncio.to_thread(_execute, code, bundle), timeout=EXEC_TIMEOUT_SECONDS)


def preview(result: Any, limit: int = 30) -> tuple[str, int]:
    if isinstance(result, pd.DataFrame):
        frame = result.head(limit)
        return frame.to_string(index=False, max_colwidth=32), int(len(result))
    if isinstance(result, pd.Series):
        frame = result.head(limit).to_frame(name=result.name or "value").reset_index()
        return frame.to_string(index=False, max_colwidth=32), int(len(result))
    return str(result), 1


def chart_points(result: Any, spec: dict[str, Any] | None) -> list[AgentChartPoint]:
    if not spec or not isinstance(result, pd.DataFrame) or result.empty:
        return []
    label_col, value_col = spec.get("label_col"), spec.get("value_col")
    if label_col not in result.columns or value_col not in result.columns:
        return []
    unit = str(spec.get("unit") or "")
    points: list[AgentChartPoint] = []
    for _, row in result.head(8).iterrows():
        try:
            value = float(row[value_col])
        except (TypeError, ValueError):
            continue
        if np.isnan(value):
            continue
        points.append(AgentChartPoint(label=str(row[label_col])[:24], value=num(value), unit=unit))
    return points


async def stream_explanation(question: str, code: str, result_text: str, rows: int, session_id: str) -> AsyncIterator[str]:
    from emergentintegrations.llm.chat import StreamDone, TextDelta, UserMessage

    chat = _chat(EXPLAIN_SYSTEM, f"{session_id}-explain")
    prompt = f"Question: {question}\n\nCode that ran:\n{code}\n\nResult ({rows} row(s), first 30 shown):\n{result_text}"
    async for event in chat.stream_message(UserMessage(text=prompt)):
        if isinstance(event, TextDelta):
            yield event.content
        elif isinstance(event, StreamDone):
            break


async def plan_and_execute(question: str, crop: str, session_id: str, full_bundle: DatasetBundle, date_from: str | None, date_to: str | None) -> tuple[dict[str, Any], Any]:
    """Generate code, run it, and retry once with the error if it fails."""
    bundle = filter_bundle(full_bundle, date_from, date_to)
    plan = await generate_code(question, crop, session_id)
    try:
        result = await run_code(plan["code"], bundle)
    except (Exception, asyncio.TimeoutError) as exc:  # noqa: BLE001 - surface any failure to the model for one repair round
        logger.info("AgentIQ code failed, retrying: %s", exc)
        plan = await generate_code(question, crop, session_id, previous_error=f"{type(exc).__name__}: {exc}", previous_code=plan["code"])
        result = await run_code(plan["code"], bundle)
    return plan, result

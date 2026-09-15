import { useState } from "react";

export default function AIAgentPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function askAgent() {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch("http://127.0.0.1:8000/agent/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Agent request failed");
      }

      setAnswer(data.answer || JSON.stringify(data));
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h2>AI Supply Chain Agent</h2>

      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask about prices, delays, crops, or mandis..."
        rows={4}
      />

      <button onClick={askAgent} disabled={loading}>
        {loading ? "Asking..." : "Ask AI Agent"}
      </button>

      {answer && (
        <p>
          <strong>Agent:</strong> {answer}
        </p>
      )}
    </section>
  );
}
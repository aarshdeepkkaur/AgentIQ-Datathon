import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, ChevronDown, ChevronRight, Code2, Loader2, MessageCircle, Send, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { AgentAnswer, AgentChartPoint, AgentHistoryResponse, AgentStreamEvent, CropName, DateWindow } from "@/data/types";
import { apiGet, apiPostStream } from "@/lib/api";

interface AskAgentIqDrawerProps { open: boolean; onClose: () => void; crop: CropName; window: DateWindow; }
interface Message { id: string; role: "user" | "agent"; text: string; evidence?: string[]; chart?: AgentChartPoint[]; mode?: "llm" | "rules" | null; code?: string | null; resultPreview?: string | null; stage?: string; streaming?: boolean; }

const SUGGESTIONS = ["Which 5 mandis have the highest average modal price for this crop?", "Show mandis where this crop is below MSP", "Which warehouse has the most trips delayed over 24 hours?", "How do monthly arrivals compare with monthly rainfall?"];
const SESSION_KEY = "agentiq-session-id";
const sessionId = () => { let value = localStorage.getItem(SESSION_KEY); if (!value) { value = crypto.randomUUID(); localStorage.setItem(SESSION_KEY, value); } return value; };
const STAGE_LABEL: Record<string, string> = { planning: "Claude is writing a pandas query…", executed: "Query ran · explaining the result…", fallback: "LLM unavailable · answering from rule-based analysis…" };

export function AskAgentIqDrawer({ open, onClose, crop, window }: AskAgentIqDrawerProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, setPending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const session = sessionId();
  const historyQuery = useQuery<AgentHistoryResponse>({ queryKey: ["agent-history", session], queryFn: () => apiGet<AgentHistoryResponse>(`/agent/history/${session}`), enabled: open, staleTime: Infinity });
  useEffect(() => {
    if (!historyQuery.data) return;
    setMessages(historyQuery.data.messages.map((item) => ({ id: item.id, role: item.role, text: item.text, evidence: item.evidence, chart: item.chart, mode: item.mode, code: item.code, resultPreview: item.result_preview })));
  }, [historyQuery.data]);
  useEffect(() => { listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" }); }, [messages, pending]);
  if (!open) return null;

  const patchLast = (patch: Partial<Message> | ((current: Message) => Partial<Message>)) => setMessages((current) => { const last = current[current.length - 1]; if (!last || last.role !== "agent") return current; const update = typeof patch === "function" ? patch(last) : patch; return [...current.slice(0, -1), { ...last, ...update }]; });

  const submit = async (question: string) => {
    const next = question.trim();
    if (!next || pending) return;
    setInput("");
    setPending(true);
    const agentId = crypto.randomUUID();
    setMessages((current) => [...current, { id: crypto.randomUUID(), role: "user", text: next }, { id: agentId, role: "agent", text: "", stage: "planning", streaming: true }]);
    try {
      await apiPostStream<AgentStreamEvent>("/agent/ask/stream", { query: next, crop_name: crop, session_id: session, date_from: window.from || null, date_to: window.to || null }, (event) => {
        if (event.event === "stage") patchLast(event.stage === "executed" ? { stage: "executed", code: event.code, resultPreview: event.preview } : { stage: event.stage });
        else if (event.event === "token") patchLast((last) => ({ text: last.text + event.text }));
        else if (event.event === "done") { const answer: AgentAnswer = event.answer; patchLast({ text: answer.answer, evidence: answer.evidence, chart: answer.chart, mode: answer.mode, code: answer.code, resultPreview: answer.result_preview, stage: undefined, streaming: false }); }
      });
    } catch {
      patchLast({ text: "AgentIQ could not reach the analysis service. Your dashboard data is still available; please try again shortly.", stage: undefined, streaming: false, mode: null });
    } finally {
      setPending(false);
      queryClient.invalidateQueries({ queryKey: ["agent-history", session] });
    }
  };

  return <div className="fixed inset-0 z-[60] bg-[#07111F]/65 backdrop-blur-sm" onClick={onClose} data-testid="ask-agentiq-overlay"><aside className="absolute right-0 top-0 flex h-full w-full max-w-lg flex-col border-l border-[#A5F36B]/15 bg-[#081522] shadow-[-20px_0_80px_rgba(0,0,0,.28)]" onClick={(event) => event.stopPropagation()} data-testid="ask-agentiq-chat-drawer">
    <div className="flex items-start justify-between border-b border-white/[0.07] p-5"><div className="flex items-center gap-3"><div className="relative flex size-10 items-center justify-center rounded-2xl bg-[#A5F36B]/10 text-[#A5F36B]"><Bot className="size-5" /><span className="absolute -right-1 -top-1 size-2 rounded-full bg-[#A5F36B] shadow-[0_0_8px_#A5F36B]" /></div><div><div className="flex items-center gap-2"><h2 className="text-base font-semibold text-white" data-testid="ask-agentiq-title">Ask AgentIQ</h2><Sparkles className="size-3.5 text-[#F4C86B]" /></div><p className="mt-1 text-[10px] text-[#8CA0B5]" data-testid="ask-agentiq-status">Context: {crop}{window.from || window.to ? ` · ${window.from || "start"} → ${window.to || "end"}` : ""} · Claude Sonnet 4.5 writes pandas over the cleaned datasets</p></div></div><Button variant="ghost" size="icon-sm" className="text-[#8CA0B5]" onClick={onClose} data-testid="ask-agentiq-close-button" aria-label="Close Ask AgentIQ"><X /></Button></div>
    <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto p-5" data-testid="ask-agentiq-message-list">
      {historyQuery.isPending && <div className="flex items-center gap-2 text-xs text-[#8CA0B5]" data-testid="ask-agentiq-history-loading"><Loader2 className="size-3.5 animate-spin text-[#A5F36B]" /> Loading your conversation…</div>}
      {!historyQuery.isPending && messages.length === 0 && <div className="rounded-2xl rounded-bl-md border border-[#69C7F5]/15 bg-[#102235] px-3.5 py-3 text-xs leading-relaxed text-[#E2E8F0]" data-testid="ask-agentiq-message-agent-0">I analyse the five cleaned datasets for {crop}: I write a pandas query for your question, run it, and explain the numbers. Ask about prices vs MSP, arrivals, routes, or weather.</div>}
      {messages.map((message, index) => <div key={message.id} className={`flex gap-2 ${message.role === "user" ? "justify-end" : ""}`} data-testid={`ask-agentiq-message-${message.role}-${index}`}><div className={`max-w-[92%] rounded-2xl px-3.5 py-3 text-xs leading-relaxed ${message.role === "user" ? "rounded-br-md bg-[#A5F36B] text-[#07111F]" : "rounded-bl-md border border-[#69C7F5]/15 bg-[#102235] text-[#E2E8F0]"}`}>
        {message.stage && <p className="mb-2 flex items-center gap-2 text-[10px] text-[#69C7F5]" data-testid={`ask-agentiq-stage-${index}`}><Loader2 className="size-3 animate-spin" /> {STAGE_LABEL[message.stage] ?? message.stage}</p>}
        {message.text && <p className="whitespace-pre-wrap">{message.text}{message.streaming && message.text && <span className="ml-0.5 inline-block h-3 w-1.5 animate-pulse bg-[#A5F36B] align-middle" />}</p>}
        {message.code && <CodeBlock code={message.code} preview={message.resultPreview ?? undefined} index={index} />}
        {message.chart && message.chart.length > 0 && <MiniChart points={message.chart} index={index} />}
        {message.evidence && message.evidence.length > 0 && <div className="mt-3 space-y-1 border-t border-white/10 pt-2" data-testid={`ask-agentiq-evidence-${index}`}>{message.evidence.map((item) => <p key={item} className="text-[10px] text-[#8CA0B5]">· {item}</p>)}</div>}
        {message.role === "agent" && message.mode && !message.streaming && <p className="mt-2 font-mono text-[8px] uppercase tracking-wider text-[#5B738B]" data-testid={`ask-agentiq-mode-${index}`}>{message.mode === "llm" ? "claude-sonnet-4.5 · pandas" : "rule-based fallback"}</p>}
      </div></div>)}
      <div className="pt-3"><p className="mb-2 flex items-center gap-2 font-mono text-[9px] uppercase tracking-wider text-[#5B738B]" data-testid="ask-agentiq-suggestions-label"><MessageCircle className="size-3" /> Suggested prompts</p><div className="space-y-2">{SUGGESTIONS.map((suggestion) => <button key={suggestion} onClick={() => submit(suggestion)} disabled={pending} className="flex w-full items-center justify-between rounded-xl border border-white/[0.07] bg-white/[0.02] px-3 py-2.5 text-left text-[11px] text-[#8CA0B5] transition-colors hover:border-[#A5F36B]/25 hover:text-white disabled:opacity-50" data-testid={`ask-agentiq-suggestion-${suggestion.slice(0, 12).toLowerCase().replaceAll(" ", "-").replaceAll("?", "")}`}>{suggestion}<ChevronRight className="size-3 text-[#5B738B]" /></button>)}</div></div>
    </div>
    <div className="border-t border-white/[0.07] p-5"><div className="flex items-center gap-2 rounded-xl border border-[#69C7F5]/20 bg-[#102235]/65 p-2 focus-within:border-[#A5F36B]/40"><Input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") submit(input); }} placeholder="Ask anything about the supply chain data…" className="h-8 border-0 bg-transparent text-xs shadow-none focus-visible:ring-0" data-testid="ask-agentiq-input" /><Button size="icon-sm" onClick={() => submit(input)} disabled={pending} className="size-8 bg-[#A5F36B] text-[#07111F] hover:bg-[#B8F7A1]" data-testid="ask-agentiq-submit-button" aria-label="Send question">{pending ? <Loader2 className="size-3.5 animate-spin" /> : <Send className="size-3.5" />}</Button></div><p className="mt-3 text-center text-[9px] text-[#4B6178]" data-testid="ask-agentiq-disclaimer">Generated pandas runs in a restricted sandbox over the loaded datasets · answers cite computed results only.</p></div>
  </aside></div>;
}

function CodeBlock({ code, preview, index }: { code: string; preview?: string; index: number }) {
  const [openCode, setOpenCode] = useState(false);
  return <div className="mt-3 rounded-lg border border-white/10 bg-[#07111F]/70" data-testid={`ask-agentiq-code-${index}`}><button type="button" onClick={() => setOpenCode((current) => !current)} className="flex w-full items-center justify-between px-3 py-2 text-[10px] text-[#69C7F5]" data-testid={`ask-agentiq-code-toggle-${index}`}><span className="flex items-center gap-1.5"><Code2 className="size-3" /> {openCode ? "Hide" : "Show"} generated pandas query</span><ChevronDown className={`size-3 transition-transform ${openCode ? "rotate-180" : ""}`} /></button>{openCode && <div className="border-t border-white/10 p-3"><pre className="max-h-48 overflow-auto whitespace-pre-wrap font-mono text-[10px] leading-relaxed text-[#B8F7A1]">{code}</pre>{preview && <><p className="mt-3 font-mono text-[8px] uppercase tracking-wider text-[#5B738B]">Result preview</p><pre className="mt-1 max-h-40 overflow-auto font-mono text-[9px] leading-relaxed text-[#C7D2DE]">{preview}</pre></>}</div>}</div>;
}

function MiniChart({ points, index }: { points: AgentChartPoint[]; index: number }) {
  const max = Math.max(...points.map((point) => Math.abs(point.value)), 1);
  return <div className="mt-3 space-y-1.5 border-t border-white/10 pt-3" data-testid={`ask-agentiq-chart-${index}`}>{points.map((point) => <div key={`${point.label}-${point.value}`} className="flex items-center gap-2 text-[10px]"><span className="w-24 shrink-0 truncate font-mono text-[#8CA0B5]" title={point.label}>{point.label}</span><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]"><div className={`h-full rounded-full ${point.value < 0 ? "bg-[#FF8585]" : "bg-[#A5F36B]"}`} style={{ width: `${Math.max(4, (Math.abs(point.value) / max) * 100)}%` }} /></div><span className="w-20 shrink-0 text-right font-mono text-white">{point.unit === "₹" ? `₹${point.value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}` : `${point.value.toLocaleString("en-IN", { maximumFractionDigits: 1 })}${point.unit ? ` ${point.unit}` : ""}`}</span></div>)}</div>;
}

import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Bot, ChevronRight, Loader2, MessageCircle, Send, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { AgentAnswer, AgentChartPoint, CropName } from "@/data/types";
import { apiPost } from "@/lib/api";

interface AskAgentIqDrawerProps { open: boolean; onClose: () => void; crop: CropName; }
interface Message { role: "user" | "agent"; text: string; evidence?: string[]; chart?: AgentChartPoint[]; }

const SUGGESTIONS = ["Show mandis where this crop is below MSP", "Which mandi has the lowest transit time?", "Compare prices across Punjab mandis", "What is the current weather signal?"];

export function AskAgentIqDrawer({ open, onClose, crop }: AskAgentIqDrawerProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([{ role: "agent", text: `I’m grounded in the synced cleaned data for ${crop}. Ask about MSP risk, route health, weather impact, or crop comparisons.` }]);
  useEffect(() => {
    setMessages([{ role: "agent", text: `I’m grounded in the synced cleaned data for ${crop}. Ask about MSP risk, route health, weather impact, or crop comparisons.` }]);
  }, [crop]);
  const askMutation = useMutation<AgentAnswer, Error, string>({
    mutationFn: (query) => apiPost<AgentAnswer>("/agent/ask", { query, crop_name: crop }),
    onSuccess: (result) => setMessages((current) => [...current, { role: "agent", text: result.answer, evidence: result.evidence, chart: result.chart }]),
    onError: () => setMessages((current) => [...current, { role: "agent", text: "The grounded agent is temporarily unavailable. Your dashboard data is still available; please try this question again shortly." }]),
  });
  if (!open) return null;
  const submit = (question: string) => {
    const next = question.trim();
    if (!next || askMutation.isPending) return;
    setInput("");
    setMessages((current) => [...current, { role: "user", text: next }]);
    askMutation.mutate(next);
  };
  return <div className="fixed inset-0 z-[60] bg-[#07111F]/65 backdrop-blur-sm" onClick={onClose} data-testid="ask-agentiq-overlay"><aside className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col border-l border-[#A5F36B]/15 bg-[#081522] shadow-[-20px_0_80px_rgba(0,0,0,.28)]" onClick={(event) => event.stopPropagation()} data-testid="ask-agentiq-chat-drawer"><div className="flex items-start justify-between border-b border-white/[0.07] p-5"><div className="flex items-center gap-3"><div className="relative flex size-10 items-center justify-center rounded-2xl bg-[#A5F36B]/10 text-[#A5F36B]"><Bot className="size-5" /><span className="absolute -right-1 -top-1 size-2 rounded-full bg-[#A5F36B] shadow-[0_0_8px_#A5F36B]" /></div><div><div className="flex items-center gap-2"><h2 className="text-base font-semibold text-white" data-testid="ask-agentiq-title">Ask AgentIQ</h2><Sparkles className="size-3.5 text-[#F4C86B]" /></div><p className="mt-1 text-[10px] text-[#8CA0B5]" data-testid="ask-agentiq-status">Context: {crop} · Grounded FastAPI · GitHub cleaned data</p></div></div><Button variant="ghost" size="icon-sm" className="text-[#8CA0B5]" onClick={onClose} data-testid="ask-agentiq-close-button" aria-label="Close Ask AgentIQ"><X /></Button></div><div className="flex-1 space-y-4 overflow-y-auto p-5" data-testid="ask-agentiq-message-list">{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`flex gap-2 ${message.role === "user" ? "justify-end" : ""}`} data-testid={`ask-agentiq-message-${message.role}-${index}`}><div className={`max-w-[88%] rounded-2xl px-3.5 py-3 text-xs leading-relaxed ${message.role === "user" ? "rounded-br-md bg-[#A5F36B] text-[#07111F]" : "rounded-bl-md border border-[#69C7F5]/15 bg-[#102235] text-[#E2E8F0]"}`}><p>{message.text}</p>{message.chart && message.chart.length > 0 && <MiniChart points={message.chart} index={index} />}{message.evidence && <div className="mt-3 space-y-1 border-t border-white/10 pt-2" data-testid={`ask-agentiq-evidence-${index}`}>{message.evidence.map((item) => <p key={item} className="text-[10px] text-[#8CA0B5]">· {item}</p>)}</div>}</div></div>)}{askMutation.isPending && <div className="flex items-center gap-2 text-xs text-[#8CA0B5]" data-testid="ask-agentiq-loading"><Loader2 className="size-3.5 animate-spin text-[#A5F36B]" /> AgentIQ is querying the cleaned datasets…</div>}<div className="pt-3"><p className="mb-2 flex items-center gap-2 font-mono text-[9px] uppercase tracking-wider text-[#5B738B]" data-testid="ask-agentiq-suggestions-label"><MessageCircle className="size-3" /> Suggested prompts</p><div className="space-y-2">{SUGGESTIONS.map((suggestion) => <button key={suggestion} onClick={() => submit(suggestion)} className="flex w-full items-center justify-between rounded-xl border border-white/[0.07] bg-white/[0.02] px-3 py-2.5 text-left text-[11px] text-[#8CA0B5] transition-colors hover:border-[#A5F36B]/25 hover:text-white" data-testid={`ask-agentiq-suggestion-${suggestion.slice(0, 12).toLowerCase().replaceAll(" ", "-")}`}>{suggestion}<ChevronRight className="size-3 text-[#5B738B]" /></button>)}</div></div></div><div className="border-t border-white/[0.07] p-5"><div className="flex items-center gap-2 rounded-xl border border-[#69C7F5]/20 bg-[#102235]/65 p-2 focus-within:border-[#A5F36B]/40"><Input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") submit(input); }} placeholder="Ask about the supply chain…" className="h-8 border-0 bg-transparent text-xs shadow-none focus-visible:ring-0" data-testid="ask-agentiq-input" /><Button size="icon-sm" onClick={() => submit(input)} disabled={askMutation.isPending} className="size-8 bg-[#A5F36B] text-[#07111F] hover:bg-[#B8F7A1]" data-testid="ask-agentiq-submit-button" aria-label="Send question"><Send className="size-3.5" /></Button></div><p className="mt-3 text-center text-[9px] text-[#4B6178]" data-testid="ask-agentiq-disclaimer">Answers are computed by FastAPI from the synced cleaned data.</p></div></aside></div>;
}
function MiniChart({ points, index }: { points: AgentChartPoint[]; index: number }) {
  const max = Math.max(...points.map((point) => Math.abs(point.value)), 1);
  return <div className="mt-3 space-y-1.5 border-t border-white/10 pt-3" data-testid={`ask-agentiq-chart-${index}`}>{points.map((point) => <div key={point.label} className="flex items-center gap-2 text-[10px]"><span className="w-16 shrink-0 truncate font-mono text-[#8CA0B5]">{point.label}</span><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]"><div className={`h-full rounded-full ${point.value < 0 ? "bg-[#FF8585]" : "bg-[#A5F36B]"}`} style={{ width: `${Math.max(4, (Math.abs(point.value) / max) * 100)}%` }} /></div><span className="w-16 shrink-0 text-right font-mono text-white">{point.unit === "₹" ? `₹${point.value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}` : `${point.value.toLocaleString("en-IN", { maximumFractionDigits: 1 })}${point.unit}`}</span></div>)}</div>;
}

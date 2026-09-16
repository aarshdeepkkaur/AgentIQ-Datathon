import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AlertTriangle, Bell, CheckCheck, Clock3, TrendingDown, Truck } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { apiGet } from "@/lib/api";
import type { AlertsResponse, CropName, DateWindow, RiskAlert } from "@/data/types";
import { formatDate, windowQuery } from "@/data/types";

interface AlertsBellProps { crop: CropName; window: DateWindow; }

const READ_KEY = "agentiq-read-alerts";
const readIds = (): Set<string> => { try { return new Set(JSON.parse(localStorage.getItem(READ_KEY) ?? "[]") as string[]); } catch { return new Set(); } };

export function AlertsBell({ crop, window }: AlertsBellProps) {
  const [read, setRead] = useState<Set<string>>(readIds);
  const [open, setOpen] = useState(false);
  const alertsQuery = useQuery<AlertsResponse>({
    queryKey: ["alerts", crop, window.from, window.to],
    queryFn: () => apiGet<AlertsResponse>(`/alerts?crop=${encodeURIComponent(crop)}${windowQuery(window)}`),
    refetchInterval: 60 * 1000,
    staleTime: 30 * 1000,
  });
  const alerts = alertsQuery.data?.alerts ?? [];
  const unread = useMemo(() => alerts.filter((alert) => !read.has(alert.id)), [alerts, read]);
  useEffect(() => {
    if (!alertsQuery.data || alertsQuery.isPlaceholderData) return;
    const fresh = unread.filter((alert) => alert.severity === "high").slice(0, 2);
    const seenKey = `agentiq-toasted-${crop}-${window.from}-${window.to}`;
    if (fresh.length && !sessionStorage.getItem(seenKey)) {
      sessionStorage.setItem(seenKey, "1");
      toast.warning(`${unread.length} new ${crop} risk alert${unread.length === 1 ? "" : "s"}`, { description: fresh[0]?.title, id: seenKey });
    }
  }, [alertsQuery.data, alertsQuery.isPlaceholderData, crop, unread, window.from, window.to]);

  const persist = (next: Set<string>) => { setRead(next); localStorage.setItem(READ_KEY, JSON.stringify([...next])); };
  const markAllRead = () => persist(new Set([...read, ...alerts.map((alert) => alert.id)]));
  const markRead = (id: string) => { if (!read.has(id)) persist(new Set([...read, id])); };

  return <Popover open={open} onOpenChange={setOpen}>
    <PopoverTrigger>
      <Button variant="ghost" size="icon" className="relative border border-white/[0.07] bg-white/[0.02] text-[#8CA0B5] hover:text-white" data-testid="header-notifications-button" aria-label={`Risk alerts, ${unread.length} unread`}>
        <Bell className="size-4" />
        {unread.length > 0 && <span className="absolute -right-1 -top-1 flex min-w-4 items-center justify-center rounded-full bg-[#FF8585] px-1 font-mono text-[9px] font-bold text-[#07111F]" data-testid="alerts-unread-count">{unread.length > 99 ? "99+" : unread.length}</span>}
      </Button>
    </PopoverTrigger>
    <PopoverContent align="end" sideOffset={10} className="w-[380px] max-w-[calc(100vw-2rem)] border-white/[0.08] bg-[#0B192C] p-0 text-[#E2E8F0] shadow-[0_24px_60px_rgba(0,0,0,0.45)]" data-testid="alerts-dropdown">
      <div className="flex items-center justify-between border-b border-white/[0.07] px-4 py-3"><div><p className="font-mono text-[9px] uppercase tracking-[0.16em] text-[#FF8585]">Risk alerts feed</p><p className="text-sm font-medium text-white" data-testid="alerts-summary">{alertsQuery.isPending ? "Scanning datasets…" : `${alerts.length} ${crop} alerts · ${alertsQuery.data?.high ?? 0} high`}</p></div><Button variant="ghost" size="sm" onClick={markAllRead} disabled={unread.length === 0} className="h-8 gap-1.5 text-[10px] text-[#8CA0B5] hover:text-[#A5F36B] disabled:opacity-40" data-testid="alerts-mark-all-read-button"><CheckCheck className="size-3.5" /> Mark all read</Button></div>
      <div className="max-h-[420px] overflow-y-auto" data-testid="alerts-list">
        {alertsQuery.isError && <p className="p-6 text-center text-xs text-[#FF8585]" data-testid="alerts-error-state">Could not load alerts. They will retry automatically.</p>}
        {!alertsQuery.isPending && !alertsQuery.isError && alerts.length === 0 && <p className="p-6 text-center text-xs text-[#8CA0B5]" data-testid="alerts-empty-state">No mandi is below MSP or delayed in this window.</p>}
        {alerts.map((alert) => <AlertRow key={alert.id} alert={alert} unread={!read.has(alert.id)} crop={crop} window={window} onOpen={() => { markRead(alert.id); setOpen(false); }} />)}
      </div>
      <div className="flex items-center gap-2 border-t border-white/[0.07] px-4 py-2 font-mono text-[9px] uppercase tracking-wider text-[#5B738B]"><Clock3 className="size-3" /> Recomputed every 60s from synced data{alertsQuery.data ? ` · ${new Date(alertsQuery.data.generated_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}` : ""}</div>
    </PopoverContent>
  </Popover>;
}

function AlertRow({ alert, unread, crop, window, onOpen }: { alert: RiskAlert; unread: boolean; crop: CropName; window: DateWindow; onOpen: () => void }) {
  const Icon = alert.type === "transit_delay" ? Truck : alert.type === "trend_drop" ? TrendingDown : AlertTriangle;
  const tone = alert.severity === "high" ? "text-[#FF8585] bg-[#FF8585]/10" : "text-[#F4C86B] bg-[#F4C86B]/10";
  const inner = <>
    <span className={`mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-lg ${tone}`}><Icon className="size-3.5" /></span>
    <span className="min-w-0 flex-1"><span className="flex items-center gap-2"><span className={`truncate text-xs ${unread ? "font-semibold text-white" : "text-[#C7D2DE]"}`}>{alert.title}</span>{unread && <span className="size-1.5 shrink-0 rounded-full bg-[#A5F36B]" data-testid={`alert-unread-dot-${alert.id}`} />}</span><span className="mt-0.5 block text-[10px] leading-relaxed text-[#8CA0B5]">{alert.detail}</span><span className="mt-1 flex items-center gap-2 font-mono text-[9px] uppercase tracking-wider text-[#5B738B]"><span className={alert.severity === "high" ? "text-[#FF8585]" : "text-[#F4C86B]"}>{alert.severity}</span>· {alert.state} · {formatDate(alert.occurred_at)}</span></span>
  </>;
  const className = `flex w-full items-start gap-3 border-b border-white/[0.05] px-4 py-3 text-left transition-colors hover:bg-white/[0.03] ${unread ? "bg-[#A5F36B]/[0.03]" : ""}`;
  if (!alert.mandi_id) return <div className={className} data-testid={`alert-row-${alert.id}`}>{inner}</div>;
  return <Link to={`/mandi/${alert.mandi_id}?crop=${encodeURIComponent(crop)}${windowQuery(window)}`} onClick={onOpen} className={className} data-testid={`alert-row-${alert.id}`}>{inner}</Link>;
}

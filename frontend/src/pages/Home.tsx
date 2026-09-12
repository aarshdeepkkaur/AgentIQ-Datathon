import { useMemo, useState } from "react";
import { ArrowUpRight, BrainCircuit, CircleHelp, Gauge, Leaf, ShieldCheck, Sparkles, Truck, Waves } from "lucide-react";
import { AnalyticsCharts } from "@/components/dashboard/AnalyticsCharts";
import { AgriOrbitCentralVisual } from "@/components/dashboard/AgriOrbitCentralVisual";
import { AskAgentIqDrawer } from "@/components/dashboard/AskAgentIqDrawer";
import { HeaderFilterBar } from "@/components/dashboard/HeaderFilterBar";
import { HeroLandscapeCard } from "@/components/dashboard/HeroLandscapeCard";
import { KpiMetricStrip } from "@/components/dashboard/KpiMetricStrip";
import { MandiDataTable } from "@/components/dashboard/MandiDataTable";
import { SidebarNavigation } from "@/components/dashboard/SidebarNavigation";
import type { CropName, RiskLevel } from "@/data/mockData";
import { cropProfiles, getMandiRows } from "@/data/mockData";

export default function Home() {
  const [crop, setCrop] = useState<CropName>("Wheat");
  const [state, setState] = useState("All states");
  const [mandi, setMandi] = useState("All mandis");
  const [risk, setRisk] = useState<RiskLevel | "all">("all");
  const [search, setSearch] = useState("");
  const [selectedMandiId, setSelectedMandiId] = useState("MANDI001");
  const [agentOpen, setAgentOpen] = useState(false);
  const rows = useMemo(() => getMandiRows(crop).filter((row) => (state === "All states" || row.state === state) && (mandi === "All mandis" || row.mandi_name === mandi) && (risk === "all" || row.risk === risk)), [crop, mandi, risk, state]);
  const allRows = useMemo(() => getMandiRows(crop), [crop]);
  const selected = allRows.find((row) => row.mandi_id === selectedMandiId) ?? allRows[0];
  const profile = cropProfiles[crop];

  const handleCropChange = (value: CropName) => { setCrop(value); setSelectedMandiId("MANDI001"); setMandi("All mandis"); };
  const handleMandiChange = (value: string) => { setMandi(value); const next = allRows.find((row) => row.mandi_name === value); if (next) setSelectedMandiId(next.mandi_id); };
  const resetFilters = () => { setState("All states"); setMandi("All mandis"); setRisk("all"); setSearch(""); };

  return <div className="min-h-screen bg-[#07111F] text-[#E2E8F0]" data-testid="agentiq-dashboard">
    <SidebarNavigation onAskAgent={() => setAgentOpen(true)} />
    <main className="min-h-screen lg:pl-64 xl:pl-72" data-testid="dashboard-main-content"><div className="mx-auto max-w-[1720px] space-y-6 p-4 pt-20 sm:p-6 sm:pt-20 lg:space-y-7 lg:p-8 lg:pt-8">
      <HeaderFilterBar crop={crop} state={state} mandi={mandi} risk={risk} search={search} onCropChange={handleCropChange} onStateChange={setState} onMandiChange={handleMandiChange} onRiskChange={setRisk} onSearchChange={setSearch} onReset={resetFilters} />
      <KpiMetricStrip crop={crop} />
      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12" data-testid="dashboard-central-stage"><div className="xl:col-span-7 2xl:col-span-8"><AgriOrbitCentralVisual crop={crop} rows={allRows} selectedMandiId={selectedMandiId} onSelectMandi={setSelectedMandiId} /></div><div className="xl:col-span-5 2xl:col-span-4"><HeroLandscapeCard crop={crop} selected={selected} /></div></section>
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4" data-testid="insight-cards"><InsightCard icon={Leaf} eyebrow="Crop intelligence" title={`${crop} is in focus`} text={profile.outlook} metric={profile.season} tone="green" /><InsightCard icon={Gauge} eyebrow="Mandi insight" title={`${selected.mandi_name} leads`} text={`${selected.priceGap >= 0 ? "Above" : "Below"} MSP by ₹${Math.abs(selected.priceGap)} · ${selected.risk} risk`} metric={`${(selected.arrivalQuantity / 1000).toFixed(1)}k qtl`} tone="gold" /><InsightCard icon={Truck} eyebrow="Logistics insight" title={`${selected.destinationWarehouse} route`} text={`Average transit is ${selected.transitHours} hours from ${selected.mandi_id}`} metric={selected.transitHours < profile.transit ? "Faster than avg" : "Watch route"} tone="cyan" /><InsightCard icon={Waves} eyebrow="Weather insight" title="Rainfall is actionable" text="Sensor units normalized to IST; arrival sensitivity remains positive." metric="0.54 correlation" tone="blue" /></section>
      <AnalyticsCharts crop={crop} />
      <MandiDataTable rows={rows} search={search} onSearchChange={setSearch} selectedMandiId={selectedMandiId} onSelectMandi={setSelectedMandiId} />
      <section className="flex flex-col gap-4 rounded-2xl border border-[#F4C86B]/15 bg-[#F4C86B]/[0.04] p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5" data-testid="data-quality-footnote"><div className="flex items-start gap-3"><CircleHelp className="mt-0.5 size-4 shrink-0 text-[#F4C86B]" /><div><p className="text-xs font-medium text-[#F4C86B]">Data quality note</p><p className="mt-1 max-w-3xl text-xs leading-relaxed text-[#8CA0B5]">~41.6% of arrival records had no usable quantity after cleaning. Some weather units were missing and excluded from conversions. Figures shown are the cleaned Datathon baseline.</p></div></div><div className="flex items-center gap-2 whitespace-nowrap font-mono text-[9px] uppercase tracking-wider text-[#5B738B]" data-testid="data-source-label"><ShieldCheck className="size-3.5 text-[#A5F36B]" /> Source synced · local fallback active</div></section>
      <footer className="flex flex-col gap-3 border-t border-white/[0.06] py-4 text-[10px] text-[#4B6178] sm:flex-row sm:items-center sm:justify-between" data-testid="dashboard-footer"><span>AgentIQ v0.9 · Mandi-to-Market Supply Chain Optimizer</span><span className="flex items-center gap-2"><Sparkles className="size-3 text-[#A5F36B]" /> Demo data · API integration pending <button className="ml-2 inline-flex items-center gap-1 text-[#8CA0B5] hover:text-[#A5F36B]" onClick={() => setAgentOpen(true)} data-testid="ask-agentiq-footer-button">Ask AgentIQ <ArrowUpRight className="size-3" /></button></span></footer>
    </div></main>
    <button className="fixed bottom-5 right-5 z-40 flex items-center gap-2 rounded-full border border-[#A5F36B]/30 bg-[#102235] px-4 py-3 text-xs font-medium text-[#A5F36B] shadow-[0_12px_35px_rgba(0,0,0,0.3)] transition-[transform,box-shadow] hover:-translate-y-0.5 hover:shadow-[0_15px_35px_rgba(165,243,107,0.18)]" onClick={() => setAgentOpen(true)} data-testid="ask-agentiq-trigger-button"><BrainCircuit className="size-4" /> Ask AgentIQ</button>
    <AskAgentIqDrawer open={agentOpen} onClose={() => setAgentOpen(false)} crop={crop} />
  </div>;
}

function InsightCard({ icon: Icon, eyebrow, title, text, metric, tone }: { icon: typeof Leaf; eyebrow: string; title: string; text: string; metric: string; tone: "green" | "gold" | "cyan" | "blue" }) {
  const colors = { green: "text-[#A5F36B] bg-[#A5F36B]/10", gold: "text-[#F4C86B] bg-[#F4C86B]/10", cyan: "text-[#69C7F5] bg-[#69C7F5]/10", blue: "text-[#69C7F5] bg-[#69C7F5]/10" };
  return <article className="rounded-2xl border border-white/[0.07] bg-[#102235]/45 p-4 transition-[transform,border-color] duration-200 hover:-translate-y-0.5 hover:border-white/15" data-testid={`insight-card-${eyebrow.toLowerCase().replaceAll(" ", "-")}`}><div className="flex items-start justify-between"><div className={`flex size-8 items-center justify-center rounded-xl ${colors[tone]}`}><Icon className="size-4" /></div><span className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#5B738B]"><ArrowUpRight className="size-3" /> live</span></div><p className="mt-4 font-mono text-[9px] uppercase tracking-[0.16em] text-[#8CA0B5]" data-testid={`${eyebrow.toLowerCase().replaceAll(" ", "-")}-eyebrow`}>{eyebrow}</p><h3 className="mt-1 text-sm font-medium text-white" data-testid={`${eyebrow.toLowerCase().replaceAll(" ", "-")}-title`}>{title}</h3><p className="mt-1 min-h-8 text-[11px] leading-relaxed text-[#8CA0B5]" data-testid={`${eyebrow.toLowerCase().replaceAll(" ", "-")}-description`}>{text}</p><p className="mt-3 text-[10px] font-medium text-[#E2E8F0]" data-testid={`${eyebrow.toLowerCase().replaceAll(" ", "-")}-metric`}>{metric}</p></article>;
}

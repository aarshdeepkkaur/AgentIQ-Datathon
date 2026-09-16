import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { AlertTriangle, ArrowUpRight, BrainCircuit, CircleHelp, Gauge, Leaf, Loader2, RefreshCw, ShieldCheck, Sparkles, Truck, Waves } from "lucide-react";
import { AnalyticsCharts } from "@/components/dashboard/AnalyticsCharts";
import { AgriOrbitCentralVisual } from "@/components/dashboard/AgriOrbitCentralVisual";
import { AskAgentIqDrawer } from "@/components/dashboard/AskAgentIqDrawer";
import { HeaderFilterBar } from "@/components/dashboard/HeaderFilterBar";
import { HeroLandscapeCard } from "@/components/dashboard/HeroLandscapeCard";
import { KpiMetricStrip } from "@/components/dashboard/KpiMetricStrip";
import { MandiDataTable } from "@/components/dashboard/MandiDataTable";
import { SatelliteMapView } from "@/components/dashboard/SatelliteMapView";
import { SidebarNavigation } from "@/components/dashboard/SidebarNavigation";
import { Button } from "@/components/ui/button";
import { apiGet } from "@/lib/api";
import type { CropName, DashboardResponse, DateWindow, RiskLevel } from "@/data/types";
import { CROPS, formatDate, formatInr, formatQtl, windowQuery } from "@/data/types";

export default function Home() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const paramCrop = params.get("crop");
  const crop: CropName = CROPS.includes(paramCrop as CropName) ? (paramCrop as CropName) : "Wheat";
  const window: DateWindow = { from: params.get("date_from") ?? "", to: params.get("date_to") ?? "" };
  const setCrop = (value: CropName) => setParams((current) => { current.set("crop", value); return current; });
  const applyWindow = (next: DateWindow) => setParams((current) => { if (next.from) current.set("date_from", next.from); else current.delete("date_from"); if (next.to) current.set("date_to", next.to); else current.delete("date_to"); return current; });
  const [state, setState] = useState("All states");
  const [mandi, setMandi] = useState("All mandis");
  const [risk, setRisk] = useState<RiskLevel | "all">("all");
  const [search, setSearch] = useState("");
  const [selectedMandiId, setSelectedMandiId] = useState("");
  const [agentOpen, setAgentOpen] = useState(false);
  const [mapMode, setMapMode] = useState<"orbit" | "satellite">("orbit");
  const [mapLayer, setMapLayer] = useState<"satellite" | "street">("satellite");

  const dashboardQuery = useQuery<DashboardResponse>({
    queryKey: ["dashboard", crop, window.from, window.to],
    queryFn: () => apiGet<DashboardResponse>(`/dashboard?crop=${encodeURIComponent(crop)}${windowQuery(window)}`),
    staleTime: 5 * 60 * 1000,
    retry: 1,
    placeholderData: keepPreviousData,
  });
  const data = dashboardQuery.data;
  const allRows = useMemo(() => data?.mandis ?? [], [data]);
  const rows = useMemo(
    () => allRows.filter((row) => (state === "All states" || row.state === state) && (mandi === "All mandis" || row.mandi_name === mandi) && (risk === "all" || row.risk === risk)),
    [allRows, mandi, risk, state],
  );
  useEffect(() => {
    if (allRows.length && !allRows.some((row) => row.mandi_id === selectedMandiId)) setSelectedMandiId(allRows[0].mandi_id);
  }, [allRows, selectedMandiId]);
  const selected = allRows.find((row) => row.mandi_id === selectedMandiId) ?? allRows[0];

  const handleCropChange = (value: CropName) => { setCrop(value); setMandi("All mandis"); };
  const handleMandiChange = (value: string) => { setMandi(value); const next = allRows.find((row) => row.mandi_name === value); if (next) setSelectedMandiId(next.mandi_id); };
  const resetFilters = () => { setState("All states"); setMandi("All mandis"); setRisk("all"); setSearch(""); applyWindow({ from: "", to: "" }); };
  const openMandi = (id: string) => navigate(`/mandi/${id}?crop=${encodeURIComponent(crop)}${windowQuery(window)}`);

  if (dashboardQuery.isPending) return <LoadingScreen />;
  if (dashboardQuery.isError || !data || !selected) return <ErrorScreen message={dashboardQuery.error?.message ?? "Dashboard payload was empty"} onRetry={() => dashboardQuery.refetch()} isRetrying={dashboardQuery.isFetching} />;

  const summary = data.crop_summary;
  const sourceLabel = data.source === "github-cleaned-data" ? "GitHub cleaned data" : "Bundled cleaned CSVs";
  const dataSource = `${sourceLabel} · ${data.totals.price_records.toLocaleString("en-IN")} price rows · ${data.totals.arrival_records.toLocaleString("en-IN")} arrivals`;
  const fastestWarehouse = data.warehouses[0];
  const bestMandi = allRows.reduce((best, row) => (row.price_gap > best.price_gap ? row : best), allRows[0]);
  const slowestMandi = allRows.filter((row) => row.trips > 0).reduce((worst, row) => (row.transit_hours > worst.transit_hours ? row : worst), allRows[0]);

  return <div className="reference-skin min-h-screen bg-[#07111F] text-[#E2E8F0]" data-testid="agentiq-dashboard">
    <SidebarNavigation onAskAgent={() => setAgentOpen(true)} />
    <main className="min-h-screen lg:pl-64 xl:pl-72" data-testid="dashboard-main-content"><div className="mx-auto max-w-[1720px] space-y-6 p-4 pt-20 sm:p-6 sm:pt-20 lg:space-y-7 lg:p-8 lg:pt-8">
      <HeaderFilterBar crop={crop} crops={data.crops as CropName[]} states={data.states} mandiNames={allRows.map((row) => row.mandi_name)} dateFrom={data.totals.date_from} dateTo={data.totals.date_to} window={window} onWindowApply={applyWindow} state={state} mandi={mandi} risk={risk} search={search} onCropChange={handleCropChange} onStateChange={setState} onMandiChange={handleMandiChange} onRiskChange={setRisk} onSearchChange={setSearch} onReset={resetFilters} dataSource={dataSource} isRefreshing={dashboardQuery.isFetching} />
      {summary.price_records === 0 && summary.arrival_records === 0 && <div className="flex items-center gap-3 rounded-2xl border border-[#F4C86B]/25 bg-[#F4C86B]/[0.06] px-4 py-3 text-xs text-[#F4C86B]" data-testid="window-empty-state"><AlertTriangle className="size-4 shrink-0" /> No {crop} price or arrival rows fall inside {formatDate(window.from || data.totals.date_from)} → {formatDate(window.to || data.totals.date_to)}. Widen the date window or reset the filters.</div>}
      <KpiMetricStrip summary={summary} totals={data.totals} weather={data.weather} topMandi={allRows[0]} />
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between" data-testid="central-view-controls"><div><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#8CA0B5]">Spatial intelligence</p><p className="mt-1 text-sm text-white">Trace {crop.toLowerCase()} signals across {rows.length} of {allRows.length} mandis</p></div><div className="flex items-center gap-1 rounded-xl border border-white/[0.08] bg-[#102235]/60 p-1" data-testid="central-view-toggle"><button type="button" onPointerDown={() => setMapMode("orbit")} onClick={() => setMapMode("orbit")} className={`rounded-lg px-3 py-2 text-[10px] font-medium transition-colors ${mapMode === "orbit" ? "bg-[#A5F36B] text-[#07111F]" : "text-[#8CA0B5] hover:text-white"}`} data-testid="orbit-view-toggle">Orbit view</button><button type="button" onPointerDown={() => setMapMode("satellite")} onClick={() => setMapMode("satellite")} className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-[10px] font-medium transition-colors ${mapMode === "satellite" ? "bg-[#E3A43C] text-[#172017]" : "text-[#8CA0B5] hover:text-white"}`} data-testid="satellite-view-toggle">Satellite view</button></div></div>
      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12" data-testid="dashboard-central-stage"><div className="xl:col-span-7 2xl:col-span-8">{mapMode === "orbit" ? <AgriOrbitCentralVisual crop={crop} rows={rows} totalHubs={allRows.length} warehouses={data.warehouses} selectedMandiId={selectedMandiId} onSelectMandi={setSelectedMandiId} /> : <SatelliteMapView rows={rows.length ? rows : allRows} selectedMandiId={selectedMandiId} onSelectMandi={setSelectedMandiId} layer={mapLayer} onLayerChange={setMapLayer} />}</div><div className="xl:col-span-5 2xl:col-span-4"><HeroLandscapeCard crop={crop} summary={summary} selected={selected} weather={data.weather} onOpenDetail={() => openMandi(selected.mandi_id)} /></div></section>
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4" data-testid="insight-cards">
        <InsightCard icon={Leaf} eyebrow="Crop intelligence" title={`${crop} · ${summary.season}`} text={summary.outlook} metric={`${formatQtl(summary.arrivals_qtl)} qtl · ${summary.price_records.toLocaleString("en-IN")} price rows`} tone="green" />
        <InsightCard icon={Gauge} eyebrow="Mandi insight" title={`${bestMandi.mandi_name} leads`} text={`Best spread ${bestMandi.price_gap >= 0 ? "+" : "−"}${formatInr(Math.abs(bestMandi.price_gap))} over MSP · ${selected.mandi_name} is ${selected.price_gap >= 0 ? "above" : "below"} MSP by ${formatInr(Math.abs(selected.price_gap))} (${selected.risk} risk)`} metric={`${formatQtl(selected.arrival_quantity_qtl)} qtl at ${selected.mandi_id}`} tone="gold" />
        <InsightCard icon={Truck} eyebrow="Logistics insight" title={`${fastestWarehouse?.destination_warehouse ?? "—"} clears fastest`} text={`${fastestWarehouse?.transit_hours.toFixed(2) ?? "—"} h average · slowest hub ${slowestMandi.mandi_id} at ${slowestMandi.transit_hours.toFixed(1)} h · delay rate ${data.totals.delay_rate.toFixed(2)}%`} metric={`${selected.destination_warehouse} · ${selected.transit_hours.toFixed(1)} h from ${selected.mandi_id}`} tone="cyan" />
        <InsightCard icon={Waves} eyebrow="Weather insight" title={`${data.weather.latest_temperature_c.toFixed(1)}°C · ${data.weather.latest_rainfall_mm.toFixed(1)} mm`} text={`Latest sensor day ${formatDate(data.weather.latest_reading_date)} · ${data.weather.latest_humidity_percent.toFixed(0)}% humidity · series mean ${data.weather.avg_temperature_c.toFixed(1)}°C`} metric={`r = ${data.weather.rainfall_arrivals_correlation.toFixed(2)} rainfall ↔ arrivals`} tone="blue" />
      </section>
      <AnalyticsCharts crop={crop} data={data} />
      <MandiDataTable rows={rows} totalCount={allRows.length} search={search} onSearchChange={setSearch} selectedMandiId={selectedMandiId} onSelectMandi={setSelectedMandiId} onOpenMandi={openMandi} />
      <section className="flex flex-col gap-4 rounded-2xl border border-[#F4C86B]/15 bg-[#F4C86B]/[0.04] p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5" data-testid="data-quality-footnote"><div className="flex items-start gap-3"><CircleHelp className="mt-0.5 size-4 shrink-0 text-[#F4C86B]" /><div><p className="text-xs font-medium text-[#F4C86B]">Data quality note</p><p className="mt-1 max-w-3xl text-xs leading-relaxed text-[#8CA0B5]" data-testid="data-quality-text">{data.data_quality.arrivals_missing_quantity_pct.toFixed(1)}% of arrival records have no usable quantity after cleaning; {data.data_quality.weather_missing_temperature_pct.toFixed(1)}% of temperature and {data.data_quality.weather_missing_rainfall_pct.toFixed(1)}% of rainfall readings could not be converted; {data.data_quality.prices_missing_msp_pct.toFixed(1)}% of price rows lack an MSP and {data.data_quality.transport_invalid_transit_pct.toFixed(1)}% of trips carry an invalid-transit flag. Rainfall ↔ arrivals r = {data.weather.rainfall_arrivals_correlation.toFixed(2)} (pipeline method, missing rain = 0); r = {data.weather.rainfall_arrivals_correlation_overlap.toFixed(2)} on overlapping days only.</p></div></div><div className="flex items-center gap-2 whitespace-nowrap font-mono text-[9px] uppercase tracking-wider text-[#5B738B]" data-testid="data-source-label"><ShieldCheck className="size-3.5 text-[#A5F36B]" /> {sourceLabel} · synced {new Date(data.fetched_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}</div></section>
      <footer className="flex flex-col gap-3 border-t border-white/[0.06] py-4 text-[10px] text-[#4B6178] sm:flex-row sm:items-center sm:justify-between" data-testid="dashboard-footer"><span>AgentIQ v1.1 · Mandi-to-Market Supply Chain Optimizer</span><span className="flex items-center gap-2"><Sparkles className="size-3 text-[#A5F36B]" /> Grounded FastAPI agent · {sourceLabel} <button className="ml-2 inline-flex items-center gap-1 text-[#8CA0B5] hover:text-[#A5F36B]" onClick={() => setAgentOpen(true)} data-testid="ask-agentiq-footer-button">Ask AgentIQ <ArrowUpRight className="size-3" /></button></span></footer>
    </div></main>
    <button className="fixed bottom-5 right-5 z-40 flex items-center gap-2 rounded-full border border-[#A5F36B]/30 bg-[#102235] px-4 py-3 text-xs font-medium text-[#A5F36B] shadow-[0_12px_35px_rgba(0,0,0,0.3)] transition-[transform,box-shadow] hover:-translate-y-0.5 hover:shadow-[0_15px_35px_rgba(165,243,107,0.18)]" onClick={() => setAgentOpen(true)} data-testid="ask-agentiq-trigger-button"><BrainCircuit className="size-4" /> Ask AgentIQ</button>
    <AskAgentIqDrawer open={agentOpen} onClose={() => setAgentOpen(false)} crop={crop} window={window} />
  </div>;
}

function LoadingScreen() {
  return <div className="reference-skin flex min-h-screen items-center justify-center bg-[#07111F] text-[#E2E8F0]" data-testid="dashboard-loading-state"><div className="flex flex-col items-center gap-4 text-center"><div className="relative flex size-16 items-center justify-center rounded-2xl border border-[#A5F36B]/20 bg-[#A5F36B]/10"><Loader2 className="size-7 animate-spin text-[#A5F36B]" /></div><div><p className="text-sm font-medium text-white">Syncing cleaned Datathon datasets</p><p className="mt-1 text-xs text-[#8CA0B5]">Pulling mandi master, arrivals, prices, transport and weather sensors…</p></div></div></div>;
}

function ErrorScreen({ message, onRetry, isRetrying }: { message: string; onRetry: () => void; isRetrying: boolean }) {
  return <div className="reference-skin flex min-h-screen items-center justify-center bg-[#07111F] p-6 text-[#E2E8F0]" data-testid="dashboard-error-state"><div className="max-w-md rounded-3xl border border-[#FF8585]/20 bg-[#102235]/70 p-6 text-center"><div className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-[#FF8585]/10 text-[#FF8585]"><AlertTriangle className="size-6" /></div><h2 className="mt-4 text-base font-semibold text-white">Dashboard data unavailable</h2><p className="mt-2 text-xs leading-relaxed text-[#8CA0B5]" data-testid="dashboard-error-message">{message}</p><Button onClick={onRetry} disabled={isRetrying} className="mt-5 gap-2 bg-[#A5F36B] text-[#07111F] hover:bg-[#B8F7A1]" data-testid="dashboard-retry-button"><RefreshCw className={`size-3.5 ${isRetrying ? "animate-spin" : ""}`} /> Retry sync</Button></div></div>;
}

function InsightCard({ icon: Icon, eyebrow, title, text, metric, tone }: { icon: typeof Leaf; eyebrow: string; title: string; text: string; metric: string; tone: "green" | "gold" | "cyan" | "blue" }) {
  const colors = { green: "text-[#A5F36B] bg-[#A5F36B]/10", gold: "text-[#F4C86B] bg-[#F4C86B]/10", cyan: "text-[#69C7F5] bg-[#69C7F5]/10", blue: "text-[#69C7F5] bg-[#69C7F5]/10" };
  const slug = eyebrow.toLowerCase().replaceAll(" ", "-");
  return <article className="rounded-2xl border border-white/[0.07] bg-[#102235]/45 p-4 transition-[transform,border-color] duration-200 hover:-translate-y-0.5 hover:border-white/15" data-testid={`insight-card-${slug}`}><div className="flex items-start justify-between"><div className={`flex size-8 items-center justify-center rounded-xl ${colors[tone]}`}><Icon className="size-4" /></div><span className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-wider text-[#5B738B]"><ArrowUpRight className="size-3" /> live</span></div><p className="mt-4 font-mono text-[9px] uppercase tracking-[0.16em] text-[#8CA0B5]" data-testid={`${slug}-eyebrow`}>{eyebrow}</p><h3 className="mt-1 text-sm font-medium text-white" data-testid={`${slug}-title`}>{title}</h3><p className="mt-1 min-h-8 text-[11px] leading-relaxed text-[#8CA0B5]" data-testid={`${slug}-description`}>{text}</p><p className="mt-3 text-[10px] font-medium text-[#E2E8F0]" data-testid={`${slug}-metric`}>{metric}</p></article>;
}

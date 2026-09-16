import { ArrowDownRight, ArrowUpRight, CloudRain, Gauge, Package, Store, Timer } from "lucide-react";
import type { CropSummary, MandiRow, NetworkTotals, WeatherSummary } from "@/data/types";
import { formatInr, formatQtl } from "@/data/types";

interface KpiMetricStripProps { summary: CropSummary; totals: NetworkTotals; weather: WeatherSummary; topMandi?: MandiRow; }

export function KpiMetricStrip({ summary, totals, weather, topMandi }: KpiMetricStripProps) {
  const priceGap = summary.price_gap;
  const trend = summary.trend_percentage;
  const gauges = [
    { label: "Modal price", value: formatInr(summary.modal_price), unit: "/qtl", change: `${trend > 0 ? "+" : ""}${trend.toFixed(2)}% vs prior 30d`, progress: Math.min(96, Math.max(12, (summary.modal_price / Math.max(summary.msp, summary.modal_price, 1)) * 100)), color: "#B8C979", testId: "kpi-avg-price-value" },
    { label: "Avg transit", value: summary.avg_transit_hours.toFixed(2), unit: "hrs", change: `${summary.delay_rate.toFixed(2)}% of trips over 24h`, progress: Math.min(96, (summary.avg_transit_hours / 24) * 100), color: "#E3A43C", testId: "kpi-avg-transit-value" },
    { label: "MSP risk", value: `${summary.below_msp_percentage.toFixed(2)}%`, unit: "below", change: `${summary.below_msp_records.toLocaleString("en-IN")} of ${(summary.below_msp_records + summary.above_msp_records).toLocaleString("en-IN")} records flagged`, progress: summary.below_msp_percentage, color: "#FF9B5F", testId: "kpi-below-msp-value" },
  ];
  const metrics = [
    { label: "Total arrivals", value: formatQtl(summary.arrivals_qtl), unit: "qtl", change: `${((summary.arrivals_qtl / Math.max(totals.total_arrivals_qtl, 1)) * 100).toFixed(1)}% of network`, caption: `${summary.arrival_records.toLocaleString("en-IN")} arrival rows`, tone: "green", icon: Package, testId: "kpi-total-arrivals-value" },
    { label: "Benchmark MSP", value: formatInr(summary.msp), unit: "/qtl", change: "govt floor", caption: `network avg ${formatInr(totals.avg_msp)}`, tone: "gold", icon: Gauge, testId: "kpi-avg-msp-value" },
    { label: "Price gap", value: `${priceGap >= 0 ? "+" : "−"}${formatInr(Math.abs(priceGap), 2)}`, unit: "/qtl", change: priceGap >= 0 ? "above MSP" : "below MSP", caption: "modal minus MSP", tone: priceGap >= 0 ? "green" : "red", icon: priceGap >= 0 ? ArrowUpRight : ArrowDownRight, testId: "kpi-price-gap-value" },
    { label: "Delay rate", value: `${summary.delay_rate.toFixed(2)}%`, unit: ">24h", change: `network ${totals.delay_rate.toFixed(2)}%`, caption: `${totals.transport_records.toLocaleString("en-IN")} trips parsed`, tone: "cyan", icon: Timer, testId: "kpi-delay-rate-value" },
    { label: "Rainfall corr.", value: weather.rainfall_arrivals_correlation.toFixed(2), unit: "r", change: weather.rainfall_arrivals_correlation >= 0 ? "positive" : "negative", caption: `${weather.readings_count.toLocaleString("en-IN")} sensor rows`, tone: "mint", icon: CloudRain, testId: "kpi-weather-correlation-value" },
    { label: "Active mandis", value: String(totals.active_mandis), unit: "hubs", change: topMandi ? `${topMandi.mandi_id} leads` : "network", caption: topMandi ? `${formatQtl(topMandi.arrival_quantity_qtl)} qtl top volume` : "monitored network", tone: "gold", icon: Store, testId: "kpi-active-mandis-value" },
  ] as const;
  const toneMap = { green: "text-[#A5F36B] bg-[#A5F36B]/[0.08]", cyan: "text-[#69C7F5] bg-[#69C7F5]/[0.08]", gold: "text-[#F4C86B] bg-[#F4C86B]/[0.08]", red: "text-[#FF8585] bg-[#FF8585]/[0.08]", mint: "text-[#B8F7A1] bg-[#B8F7A1]/[0.08]" };
  return <section className="space-y-3" data-testid="kpi-metric-strip">
    <div className="grid grid-cols-1 gap-3 md:grid-cols-3" data-testid="kpi-gauge-panels">
      {gauges.map(({ label, value, unit, change, progress, color, testId }) => <article key={label} className="group relative flex min-h-[174px] items-center gap-4 overflow-hidden rounded-2xl border border-white/[0.07] bg-[#102235]/55 p-4 transition-[transform,border-color,box-shadow] duration-200 hover:-translate-y-0.5 hover:border-[#A5F36B]/25 hover:shadow-[0_12px_30px_rgba(0,0,0,0.14)]" data-testid={`gauge-panel-${label.toLowerCase().replaceAll(" ", "-")}`}>
        <div className="relative flex size-32 shrink-0 items-center justify-center"><svg viewBox="0 0 120 120" className="size-full -rotate-90"><circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="8" /><circle cx="60" cy="60" r="48" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" strokeDasharray={`${progress * 3.02} 302`} className="gauge-ring" /></svg><div className="absolute inset-0 flex flex-col items-center justify-center"><span className="font-mono text-xl font-bold tracking-tight text-white" data-testid={testId}>{value}</span><span className="text-[9px] text-[#8CA0B5]">{unit}</span></div></div><div className="min-w-0"><p className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#8CA0B5]" data-testid={`${testId}-label`}>{label}</p><p className="mt-3 text-xs font-medium text-white" data-testid={`${testId}-change`}>{change}</p><div className="mt-3 flex items-center gap-2 text-[10px] text-[#5B738B]"><span className="size-1.5 rounded-full" style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}` }} /> {summary.crop_name} signal</div></div><span className="pointer-events-none absolute -right-8 -top-8 size-32 rounded-full opacity-10" style={{ backgroundColor: color }} />
      </article>)}
    </div>
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6" data-testid="kpi-compact-panels">
    {metrics.map(({ label, value, unit, change, caption, tone, icon: Icon, testId }) => <article key={label} className="group rounded-2xl border border-white/[0.07] bg-[#102235]/55 p-4 transition-[transform,border-color,box-shadow] duration-200 hover:-translate-y-0.5 hover:border-[#A5F36B]/25 hover:shadow-[0_12px_30px_rgba(0,0,0,0.14)]" data-testid={`kpi-card-${label.toLowerCase().replaceAll(" ", "-").replaceAll(".", "")}`}>
      <div className="mb-4 flex items-start justify-between"><span className={`flex size-7 items-center justify-center rounded-lg ${toneMap[tone]}`}><Icon className="size-3.5" /></span><span className={`truncate pl-2 font-mono text-[9px] ${toneMap[tone].split(" ")[0]}`}>{change}</span></div>
      <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-[#8CA0B5]" data-testid={`${testId}-label`}>{label}</p>
      <div className="mt-1 flex items-baseline gap-1" data-testid={testId}><span className="font-mono text-xl font-bold tracking-tight text-white sm:text-2xl">{value}</span><span className="text-[10px] text-[#8CA0B5]">{unit}</span></div>
      <p className="mt-2 truncate text-[10px] text-[#4B6178]" data-testid={`${testId}-caption`}>{caption}</p>
    </article>)}
    </div>
  </section>;
}

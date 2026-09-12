import { ArrowDownRight, ArrowUpRight, CloudRain, Gauge, IndianRupee, Package, Route, Store, TriangleAlert } from "lucide-react";
import type { CropName } from "@/data/mockData";
import { cropProfiles } from "@/data/mockData";

interface KpiMetricStripProps { crop: CropName; }

export function KpiMetricStrip({ crop }: KpiMetricStripProps) {
  const profile = cropProfiles[crop];
  const priceGap = profile.modal - profile.msp;
  const metrics = [
    { label: "Total arrivals", value: `${(profile.arrivals / 1000000).toFixed(2)}M`, unit: "qtl", change: "+4.8%", caption: "cleaned volume", tone: "green", icon: Package, testId: "kpi-total-arrivals-value" },
    { label: "Avg modal price", value: `₹${profile.modal.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`, unit: "/qtl", change: `${profile.trend > 0 ? "+" : ""}${profile.trend}%`, caption: "market signal", tone: "cyan", icon: IndianRupee, testId: "kpi-avg-price-value" },
    { label: "Benchmark MSP", value: `₹${profile.msp.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`, unit: "/qtl", change: "govt floor", caption: "reference value", tone: "gold", icon: Gauge, testId: "kpi-avg-msp-value" },
    { label: "Price gap", value: `${priceGap >= 0 ? "+" : "−"}₹${Math.abs(priceGap)}`, unit: "/qtl", change: priceGap >= 0 ? "above MSP" : "below MSP", caption: "modal minus MSP", tone: priceGap >= 0 ? "green" : "red", icon: priceGap >= 0 ? ArrowUpRight : ArrowDownRight, testId: "kpi-price-gap-value" },
    { label: "Avg transit", value: profile.transit.toFixed(2), unit: "hrs", change: "−0.6%", caption: "across routes", tone: "cyan", icon: Route, testId: "kpi-avg-transit-value" },
    { label: "Below MSP", value: `${profile.belowMsp.toFixed(2)}%`, unit: "records", change: "9,131 flagged", caption: "risk watch", tone: "red", icon: TriangleAlert, testId: "kpi-below-msp-value" },
    { label: "Rainfall corr.", value: "0.54", unit: "r", change: "positive", caption: "arrival sensitivity", tone: "mint", icon: CloudRain, testId: "kpi-weather-correlation-value" },
    { label: "Active mandis", value: "57", unit: "hubs", change: "MANDI001 lead", caption: "monitored network", tone: "gold", icon: Store, testId: "kpi-active-mandis-value" },
  ] as const;
  const toneMap = { green: "text-[#A5F36B] bg-[#A5F36B]/[0.08]", cyan: "text-[#69C7F5] bg-[#69C7F5]/[0.08]", gold: "text-[#F4C86B] bg-[#F4C86B]/[0.08]", red: "text-[#FF8585] bg-[#FF8585]/[0.08]", mint: "text-[#B8F7A1] bg-[#B8F7A1]/[0.08]" };
  return <section className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-8" data-testid="kpi-metric-strip">
    {metrics.map(({ label, value, unit, change, caption, tone, icon: Icon, testId }) => <article key={label} className="group rounded-2xl border border-white/[0.07] bg-[#102235]/55 p-4 transition-[transform,border-color,box-shadow] duration-200 hover:-translate-y-0.5 hover:border-[#A5F36B]/25 hover:shadow-[0_12px_30px_rgba(0,0,0,0.14)]" data-testid={`kpi-card-${label.toLowerCase().replaceAll(" ", "-").replaceAll(".", "")}`}>
      <div className="mb-4 flex items-start justify-between"><span className={`flex size-7 items-center justify-center rounded-lg ${toneMap[tone]}`}><Icon className="size-3.5" /></span><span className={`font-mono text-[9px] ${toneMap[tone].split(" ")[0]}`}>{change}</span></div>
      <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-[#8CA0B5]" data-testid={`${testId}-label`}>{label}</p>
      <div className="mt-1 flex items-baseline gap-1" data-testid={testId}><span className="font-mono text-xl font-bold tracking-tight text-white sm:text-2xl">{value}</span><span className="text-[10px] text-[#8CA0B5]">{unit}</span></div>
      <p className="mt-2 truncate text-[10px] text-[#4B6178]" data-testid={`${testId}-caption`}>{caption}</p>
    </article>)}
  </section>;
}

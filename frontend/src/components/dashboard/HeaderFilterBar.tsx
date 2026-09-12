import { Bell, CalendarDays, ChevronDown, Filter, MapPin, RotateCcw, Search, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { CropName, RiskLevel } from "@/data/mockData";
import { CROPS } from "@/data/mockData";

interface HeaderFilterBarProps {
  crop: CropName;
  state: string;
  mandi: string;
  risk: RiskLevel | "all";
  search: string;
  onCropChange: (value: CropName) => void;
  onStateChange: (value: string) => void;
  onMandiChange: (value: string) => void;
  onRiskChange: (value: RiskLevel | "all") => void;
  onSearchChange: (value: string) => void;
  onReset: () => void;
}

const STATE_OPTIONS = ["All states", "Punjab", "Uttar Pradesh", "Maharashtra", "Madhya Pradesh", "Haryana", "Rajasthan"];

export function HeaderFilterBar({ crop, state, mandi, risk, search, onCropChange, onStateChange, onMandiChange, onRiskChange, onSearchChange, onReset }: HeaderFilterBarProps) {
  return <>
    <header className="flex flex-col gap-5 border-b border-white/[0.06] pb-6 xl:flex-row xl:items-end xl:justify-between" data-testid="dashboard-header">
      <div className="pl-12 lg:pl-0" data-testid="dashboard-title-info">
        <div className="mb-3 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-[#69C7F5]" data-testid="dashboard-breadcrumb"><span className="size-1.5 rounded-full bg-[#69C7F5] shadow-[0_0_8px_#69C7F5]" /> SUPPLY CHAIN / OVERVIEW <span className="text-[#4B6178]">·</span> 06 SEP 2026</div>
        <h1 className="text-2xl font-semibold tracking-[-0.03em] text-white sm:text-3xl" data-testid="dashboard-title">Mandi-to-Market <span className="text-[#A5F36B]">Optimizer</span></h1>
        <p className="mt-1 text-sm text-[#8CA0B5]" data-testid="dashboard-subtitle">AI-powered agricultural market and logistics intelligence</p>
      </div>
      <div className="flex items-center gap-3" data-testid="dashboard-header-actions">
        <div className="hidden items-center gap-2 rounded-full border border-[#A5F36B]/20 bg-[#A5F36B]/[0.05] px-3 py-2 text-xs text-[#A5F36B] sm:flex" data-testid="live-monitoring-status"><span className="size-1.5 animate-pulse rounded-full bg-[#A5F36B]" /> Live monitoring</div>
        <Button variant="ghost" size="icon" className="border border-white/[0.07] bg-white/[0.02] text-[#8CA0B5] hover:text-white" data-testid="header-notifications-button" aria-label="View notifications"><Bell className="size-4" /><span className="absolute ml-4 mt-[-14px] size-1.5 rounded-full bg-[#FF8585]" /></Button>
        <div className="hidden items-center gap-2 border-l border-white/[0.08] pl-3 sm:flex" data-testid="header-profile"><div className="flex size-8 items-center justify-center rounded-full bg-[#1c3d47] text-[10px] font-semibold text-[#A5F36B]">AK</div><ChevronDown className="size-3 text-[#5B738B]" /></div>
      </div>
    </header>
    <section className="relative overflow-hidden rounded-2xl border border-[#69C7F5]/10 bg-[#102235]/65 p-4 shadow-[0_18px_60px_rgba(0,0,0,0.14)] backdrop-blur-xl sm:p-5" data-testid="filter-control-center">
      <div className="pointer-events-none absolute right-0 top-0 size-32 rounded-full bg-[#A5F36B]/[0.06] blur-3xl" />
      <div className="relative flex flex-col gap-4 xl:flex-row xl:items-end">
        <div className="min-w-[196px] xl:w-1/4" data-testid="crop-selector-control">
          <label className="mb-2 block font-mono text-[10px] uppercase tracking-[0.18em] text-[#8CA0B5]">Tracking crop</label>
          <Select value={crop} onValueChange={(value) => onCropChange(value as CropName)}><SelectTrigger className="h-11 w-full border-[#A5F36B]/25 bg-[#07111F]/80 text-white" data-testid="crop-selector-trigger"><SelectValue>{(value) => <span className="flex items-center gap-2"><span className="flex size-6 items-center justify-center rounded-lg bg-[#A5F36B]/15 text-[10px] font-bold text-[#A5F36B]">{value?.slice(0, 2).toUpperCase()}</span>{value}</span>}</SelectValue></SelectTrigger><SelectContent>{CROPS.map((item) => <SelectItem key={item} value={item} data-testid={`crop-selector-${item.toLowerCase()}-option`}>{item}</SelectItem>)}</SelectContent></Select>
        </div>
        <div className="grid flex-1 grid-cols-2 gap-3 sm:grid-cols-4" data-testid="filter-fields">
          <div><label className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[#8CA0B5]"><MapPin className="size-3" /> State</label><Select value={state} onValueChange={onStateChange}><SelectTrigger className="h-9 w-full border-white/[0.08] bg-[#07111F]/60 text-xs text-[#E2E8F0]" data-testid="filter-state-select"><SelectValue>{(value) => value}</SelectValue></SelectTrigger><SelectContent>{STATE_OPTIONS.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
          <div><label className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[#8CA0B5]"><StoreIcon /> Mandi</label><Select value={mandi} onValueChange={onMandiChange}><SelectTrigger className="h-9 w-full border-white/[0.08] bg-[#07111F]/60 text-xs text-[#E2E8F0]" data-testid="filter-mandi-select"><SelectValue>{(value) => value === "All mandis" ? value : value?.replace(" Mandi", "")}</SelectValue></SelectTrigger><SelectContent><SelectItem value="All mandis">All mandis</SelectItem>{["Hyderabad Mandi", "Chittoor Mandi", "Durg Market", "Nashik Agri Hub", "Indore Grain Yard", "Amritsar Agri Yard", "Jorhat Grain Market", "Kota Produce Hub"].map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
          <div><label className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[#8CA0B5]"><CalendarDays className="size-3" /> Window</label><button className="flex h-9 w-full items-center justify-between rounded-lg border border-white/[0.08] bg-[#07111F]/60 px-3 text-left text-xs text-[#E2E8F0]" data-testid="filter-date-range-button" aria-label="Choose date range"><span>01 Aug — 06 Sep</span><ChevronDown className="size-3 text-[#5B738B]" /></button></div>
          <div><label className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[#8CA0B5]"><Filter className="size-3" /> Risk level</label><Select value={risk} onValueChange={(value) => onRiskChange(value as RiskLevel | "all")}><SelectTrigger className="h-9 w-full border-white/[0.08] bg-[#07111F]/60 text-xs text-[#E2E8F0]" data-testid="filter-risk-toggle"><SelectValue>{(value) => value === "all" ? "All risk" : `${value?.slice(0, 1).toUpperCase()}${value?.slice(1)} risk`}</SelectValue></SelectTrigger><SelectContent><SelectItem value="all">All risk</SelectItem><SelectItem value="low">Low risk</SelectItem><SelectItem value="medium">Medium risk</SelectItem><SelectItem value="high">High risk</SelectItem></SelectContent></Select></div>
        </div>
        <Button variant="ghost" size="sm" onClick={onReset} className="h-9 gap-2 self-start border border-white/[0.08] text-[#8CA0B5] hover:border-[#A5F36B]/30 hover:text-[#A5F36B] xl:self-end" data-testid="filter-reset-button"><RotateCcw className="size-3.5" /> Reset</Button>
      </div>
      <div className="relative mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-white/[0.06] pt-3" data-testid="filter-summary-row"><div className="flex items-center gap-2 text-xs text-[#E2E8F0]"><SlidersHorizontal className="size-3.5 text-[#A5F36B]" /> Filters applied to all views</div><span className="h-3 w-px bg-white/10" /><div className="flex items-center gap-2 text-[11px] text-[#8CA0B5]"><Search className="size-3" /> <Input value={search} onChange={(event) => onSearchChange(event.target.value)} placeholder="Search mandis…" className="h-6 w-36 border-0 bg-transparent p-0 text-[11px] text-white shadow-none focus-visible:ring-0" data-testid="mandi-table-search-input" /></div><span className="ml-auto rounded-full border border-[#F4C86B]/20 bg-[#F4C86B]/[0.06] px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-[#F4C86B]" data-testid="data-quality-disclaimer-badge">Demo data · API integration pending</span></div>
    </section>
  </>;
}

function StoreIcon() { return <span className="flex size-3 items-center justify-center rounded-sm border border-current" />; }

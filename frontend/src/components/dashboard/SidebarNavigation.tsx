import { useState } from "react";
import { Activity, AlertTriangle, BarChart3, Bot, CloudRain, FileSpreadsheet, LayoutDashboard, Menu, Settings, Store, Truck, Wheat, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const navItems = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Mandi Analytics", icon: Store },
  { label: "Crop Intelligence", icon: Wheat },
  { label: "Logistics & Fleet", icon: Truck },
  { label: "Weather Impact", icon: CloudRain },
  { label: "Risk & MSP Gaps", icon: AlertTriangle },
  { label: "Ask AgentIQ", icon: Bot },
  { label: "Reports & Pipeline", icon: FileSpreadsheet },
];

interface SidebarNavigationProps {
  onAskAgent: () => void;
}

export function SidebarNavigation({ onAskAgent }: SidebarNavigationProps) {
  const [open, setOpen] = useState(false);
  const renderNav = () => (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-5 pb-8 pt-6">
        <div className="flex items-center gap-3" data-testid="sidebar-brand-info">
          <div className="relative flex size-10 items-center justify-center rounded-2xl bg-[#A5F36B] text-[#07111F] shadow-[0_0_25px_rgba(165,243,107,0.24)]" data-testid="sidebar-brand-mark">
            <Wheat className="size-5" strokeWidth={2.5} />
            <span className="absolute -right-1 -top-1 size-2 rounded-full bg-[#F4C86B]" />
          </div>
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#A5F36B]" data-testid="sidebar-brand-eyebrow">AGRI INTELLIGENCE</p>
            <p className="text-lg font-semibold tracking-tight text-white" data-testid="sidebar-brand-name">Agent<span className="text-[#A5F36B]">IQ</span></p>
          </div>
        </div>
        <Button variant="ghost" size="icon-sm" className="text-[#8CA0B5] lg:hidden" onClick={() => setOpen(false)} data-testid="sidebar-close-button" aria-label="Close navigation"><X /></Button>
      </div>
      <div className="px-3">
        <p className="px-3 pb-3 font-mono text-[10px] uppercase tracking-[0.2em] text-[#4B6178]" data-testid="sidebar-navigation-label">Control room</p>
        <nav className="space-y-1" aria-label="Primary navigation" data-testid="sidebar-navigation">
          {navItems.map(({ label, icon: Icon }, index) => {
            const active = index === 0;
            return <button
              key={label}
              onClick={label === "Ask AgentIQ" ? onAskAgent : undefined}
              className={`group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[13px] transition-[background,color,transform] duration-200 ${active ? "bg-[#A5F36B]/10 text-[#A5F36B] shadow-[inset_2px_0_0_#A5F36B]" : "text-[#8CA0B5] hover:bg-white/[0.04] hover:text-white hover:translate-x-0.5"}`}
              data-testid={`sidebar-nav-${label.toLowerCase().replaceAll(" ", "-").replaceAll("&", "and")}-button`}
              aria-label={label}
            >
              <Icon className={`size-4 ${active ? "text-[#A5F36B]" : "text-[#5B738B] group-hover:text-[#A5F36B]"}`} strokeWidth={active ? 2.2 : 1.8} />
              <span>{label}</span>
              {active && <span className="ml-auto size-1.5 rounded-full bg-[#A5F36B] shadow-[0_0_10px_#A5F36B]" />}
            </button>;
          })}
        </nav>
      </div>
      <div className="mt-auto space-y-3 p-4">
        <button className="flex w-full items-center gap-3 rounded-2xl border border-[#69C7F5]/15 bg-[#102235]/60 p-3 text-left" data-testid="sidebar-pipeline-status" aria-label="View pipeline status">
          <span className="relative flex size-8 items-center justify-center rounded-full bg-[#A5F36B]/10 text-[#A5F36B]"><Activity className="size-4" /><span className="absolute right-0 top-0 size-2 rounded-full bg-[#A5F36B] shadow-[0_0_8px_#A5F36B]" /></span>
          <span><span className="block text-xs font-medium text-white">System online</span><span className="block text-[10px] text-[#8CA0B5]">Pipeline active · 08:42 IST</span></span>
        </button>
        <div className="flex items-center gap-3 border-t border-white/[0.06] pt-4" data-testid="sidebar-user-profile">
          <div className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-[#F4C86B] to-[#65D68A] text-xs font-bold text-[#07111F]">AK</div>
          <div className="min-w-0 flex-1"><p className="truncate text-xs font-medium text-white">Analytics workspace</p><p className="truncate text-[10px] text-[#8CA0B5]">Datathon project</p></div>
          <Settings className="size-4 text-[#5B738B]" />
        </div>
      </div>
    </div>
  );

  return <>
    <Button variant="ghost" size="icon" className="fixed left-4 top-4 z-50 border border-white/10 bg-[#102235] text-[#A5F36B] lg:hidden" onClick={() => setOpen(true)} data-testid="sidebar-open-button" aria-label="Open navigation"><Menu /></Button>
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-[#69C7F5]/10 bg-[#081522]/95 backdrop-blur-xl lg:block xl:w-72" data-testid="sidebar-navigation-panel">{renderNav()}</aside>
    {open && <div className="fixed inset-0 z-50 bg-[#07111F]/80 backdrop-blur-sm lg:hidden" onClick={() => setOpen(false)} data-testid="sidebar-mobile-overlay"><aside className="h-full w-72 border-r border-[#69C7F5]/15 bg-[#081522]" onClick={(event) => event.stopPropagation()}>{renderNav()}</aside></div>}
  </>;
}

import { useEffect } from "react";
import { Map as MapIcon, MapPin, Satellite } from "lucide-react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";
import type { MandiRow } from "@/data/mockData";

interface SatelliteMapViewProps {
  rows: MandiRow[];
  selectedMandiId: string;
  onSelectMandi: (id: string) => void;
  layer: "satellite" | "street";
  onLayerChange: (layer: "satellite" | "street") => void;
}

function Recenter({ selected }: { selected?: MandiRow }) {
  const map = useMap();
  useEffect(() => {
    if (selected) map.flyTo([selected.latitude, selected.longitude], Math.max(map.getZoom(), 5), { duration: 0.7 });
  }, [map, selected]);
  return null;
}

export function SatelliteMapView({ rows, selectedMandiId, onSelectMandi, layer, onLayerChange }: SatelliteMapViewProps) {
  const selected = rows.find((row) => row.mandi_id === selectedMandiId) ?? rows[0];
  const center: [number, number] = selected ? [selected.latitude, selected.longitude] : [22.8, 79.0];
  const tileUrl = layer === "satellite" ? "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const attribution = layer === "satellite" ? "Tiles © Esri" : "© OpenStreetMap contributors";
  return <article className="relative min-h-[485px] overflow-hidden rounded-3xl border border-[#69C7F5]/15 bg-[#152319]" data-testid="satellite-map-view"><div className="absolute left-5 top-5 z-[500] flex items-center gap-2 rounded-xl border border-white/15 bg-[#122016]/85 px-3 py-2 text-xs text-white backdrop-blur-md" data-testid="satellite-map-title"><MapPin className="size-3.5 text-[#E3A43C]" /> Geographic network <span className="text-[10px] text-[#A4AA91]">· {rows.length} visible hubs</span></div><div className="absolute right-5 top-5 z-[500] flex gap-1 rounded-xl border border-white/15 bg-[#122016]/90 p-1 backdrop-blur-md" data-testid="satellite-map-layer-toggle"><button type="button" onPointerDown={() => onLayerChange("satellite")} onClick={() => onLayerChange("satellite")} className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[10px] ${layer === "satellite" ? "bg-[#E3A43C] text-[#152319]" : "text-[#A4AA91]"}`} data-testid="satellite-map-satellite-button"><Satellite className="size-3" /> Satellite</button><button type="button" onPointerDown={() => onLayerChange("street")} onClick={() => onLayerChange("street")} className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[10px] ${layer === "street" ? "bg-[#B8C979] text-[#152319]" : "text-[#A4AA91]"}`} data-testid="satellite-map-street-button"><MapIcon className="size-3" /> Street</button></div><MapContainer center={center} zoom={5} scrollWheelZoom className="z-0 h-[485px] w-full" data-testid="satellite-map-container"><TileLayer key={layer} url={tileUrl} attribution={attribution} maxZoom={18} /><Recenter selected={selected} />{rows.map((row) => { const selectedNode = row.mandi_id === selectedMandiId; const color = row.risk === "high" ? "#FF8585" : row.risk === "medium" ? "#E3A43C" : "#B8C979"; return <CircleMarker key={row.mandi_id} center={[row.latitude, row.longitude]} radius={selectedNode ? 11 : 7} pathOptions={{ color, fillColor: color, fillOpacity: selectedNode ? 0.9 : 0.65, weight: selectedNode ? 3 : 1.5 }} eventHandlers={{ click: () => onSelectMandi(row.mandi_id) }} data-testid={`satellite-map-pin-${row.mandi_id.toLowerCase()}`}><Popup><div className="min-w-[150px]"><strong>{row.mandi_name}</strong><br />{row.state}<br /><span>₹{row.modalPrice.toLocaleString("en-IN")} modal · {row.transitHours}h transit</span></div></Popup></CircleMarker>; })}</MapContainer><div className="absolute bottom-4 left-5 z-[500] flex items-center gap-3 rounded-xl border border-white/15 bg-[#122016]/85 px-3 py-2 font-mono text-[9px] uppercase tracking-wider text-[#A4AA91] backdrop-blur-md" data-testid="satellite-map-attribution"><span className="size-1.5 rounded-full bg-[#B8C979]" /> Live position layer <span className="text-[#707A65]">· {selected?.mandi_id ?? "—"}</span></div></article>;
}
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

type Mandi = {
  mandi_id: string;
  mandi_name: string;
  district?: string;
  state?: string;
  mandi_type?: string;
  total_area_acres?: number;
  latitude?: number;
  longitude?: number;
  risk?: string;
  destination_warehouse?: string;
  modal_price?: number;
  msp?: number;
  price_gap?: number;
  below_msp_percentage?: number;
  arrival_quantity_qtl?: number;
  farmer_count?: number;
  price_records?: number;
  arrival_records?: number;
  arrivals_missing_quantity?: number;
  transit_hours?: number;
  delay_rate?: number;
  trips?: number;
  delayed_trips?: number;
  invalid_transit_trips?: number;
  first_date?: string;
  last_date?: string;
};

export default function MandiDetail() {
  const { mandiId } = useParams<{ mandiId: string }>();

  const [mandi, setMandi] = useState<Mandi | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchMandi() {
      try {
        setLoading(true);
        setError("");

        const id = mandiId || "MANDI001";

        const response = await fetch(`${import.meta.env.VITE_API_URL || "/api"}/mandi/${id}`);

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data: Mandi = await response.json();

        setMandi(data);
      } catch (err) {
        console.error("Mandi fetch error:", err);
        setError("Unable to load mandi details.");
      } finally {
        setLoading(false);
      }
    }

    fetchMandi();
  }, [mandiId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#07111F] p-6 text-white">
        Loading mandi details...
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-[#07111F] p-6 text-red-400">
        {error}
      </main>
    );
  }

  if (!mandi) {
    return (
      <main className="min-h-screen bg-[#07111F] p-6 text-white">
        No mandi details found.
      </main>
    );
  }

  const money = (value?: number) =>
    value === undefined
      ? "—"
      : `₹${value.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      })}`;

  const number = (value?: number) =>
    value === undefined
      ? "—"
      : value.toLocaleString("en-IN", {
        maximumFractionDigits: 2,
      });

  return (
    <main className="min-h-screen bg-[#07111F] p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-[#69C7F5]">
          Mandi intelligence
        </p>

        <h1 className="mt-2 text-3xl font-bold">
          {mandi.mandi_name}
        </h1>

        <p className="mt-2 text-sm text-[#8CA0B5]">
          {mandi.mandi_id} · {mandi.district || "District unavailable"} ·{" "}
          {mandi.state || "State unavailable"} ·{" "}
          {mandi.mandi_type || "Type unavailable"}
        </p>

        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Modal price</p>
            <p className="mt-2 text-2xl font-bold">
              {money(mandi.modal_price)}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">MSP</p>
            <p className="mt-2 text-2xl font-bold">
              {money(mandi.msp)}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Price gap</p>
            <p
              className={`mt-2 text-2xl font-bold ${(mandi.price_gap || 0) >= 0
                  ? "text-[#A5F36B]"
                  : "text-[#FF8585]"
                }`}
            >
              {money(mandi.price_gap)}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Risk</p>
            <p className="mt-2 text-2xl font-bold uppercase">
              {mandi.risk || "—"}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Arrival quantity</p>
            <p className="mt-2 text-2xl font-bold">
              {number(mandi.arrival_quantity_qtl)} qtl
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Farmers</p>
            <p className="mt-2 text-2xl font-bold">
              {number(mandi.farmer_count)}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Transit time</p>
            <p className="mt-2 text-2xl font-bold">
              {mandi.transit_hours ?? "—"} hours
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-[#102235] p-5">
            <p className="text-xs text-[#8CA0B5]">Destination</p>
            <p className="mt-2 text-lg font-bold">
              {mandi.destination_warehouse || "—"}
            </p>
          </div>
        </div>

        <section className="mt-6 rounded-2xl border border-white/10 bg-[#102235] p-5">
          <h2 className="text-lg font-semibold">Additional information</h2>

          <div className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
            <p>
              <span className="text-[#8CA0B5]">Below MSP:</span>{" "}
              {mandi.below_msp_percentage ?? "—"}%
            </p>

            <p>
              <span className="text-[#8CA0B5]">Delay rate:</span>{" "}
              {mandi.delay_rate ?? "—"}%
            </p>

            <p>
              <span className="text-[#8CA0B5]">Trips:</span>{" "}
              {number(mandi.trips)}
            </p>

            <p>
              <span className="text-[#8CA0B5]">Delayed trips:</span>{" "}
              {number(mandi.delayed_trips)}
            </p>

            <p>
              <span className="text-[#8CA0B5]">Price records:</span>{" "}
              {number(mandi.price_records)}
            </p>

            <p>
              <span className="text-[#8CA0B5]">Arrival records:</span>{" "}
              {number(mandi.arrival_records)}
            </p>

            <p>
              <span className="text-[#8CA0B5]">Latitude:</span>{" "}
              {mandi.latitude ?? "—"}
            </p>

            <p>
              <span className="text-[#8CA0B5]">Longitude:</span>{" "}
              {mandi.longitude ?? "—"}
            </p>

            <p>
              <span className="text-[#8CA0B5]">Data period:</span>{" "}
              {mandi.first_date || "—"} to {mandi.last_date || "—"}
            </p>
          </div>
        </section>

        <p className="mt-5 text-xs text-[#8CA0B5]">
          Source: {mandi.mandi_id} · Crop: Wheat
        </p>
      </div>
    </main>
  );
}
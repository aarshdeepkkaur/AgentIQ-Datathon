import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

type Mandi = {
  id: string;
  name: string;
  location?: string;
  state?: string;
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

        const response = await fetch(
          `http://127.0.0.1:8000/mandis/${id}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch mandi details");
        }

        const data: Mandi = await response.json();

        setMandi(data);
      } catch (err) {
        setError("Unable to load mandi details");
      } finally {
        setLoading(false);
      }
    }

    fetchMandi();
  }, [mandiId]);

  if (loading) {
    return <div>Loading mandi details...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  if (!mandi) {
    return <div>No mandi details found.</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold">
        {mandi.name}
      </h1>

      <p className="mt-2 text-gray-600">
        {mandi.location || "Location unavailable"}
      </p>

      <p className="mt-1 text-gray-600">
        {mandi.state || "State unavailable"}
      </p>
    </div>
  );
}
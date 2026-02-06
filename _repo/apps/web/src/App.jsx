import React, { useEffect, useState } from "react";
import { useRecords } from "./store";
import { Button } from "./components/ui/button";
import { KINDS, SCHEMAS, normalize, sample } from "./schema";

export default function App() {
  const { kind, records, loading, setKind, refresh, saveRecord } = useRecords();
  const [payload, setPayload] = useState(JSON.stringify(sample("intent_aspirational"), null, 2));
  const [error, setError] = useState("");

  useEffect(() => { refresh(); }, []);
  useEffect(() => {
    setPayload(JSON.stringify(sample(kind), null, 2));
  }, [kind]);

  const onSubmit = async (e) => {
    e.preventDefault();
    let parsed;
    try {
      parsed = JSON.parse(payload);
    } catch (err) {
      setError("Invalid JSON");
      return;
    }
    const normalized = normalize(kind, parsed);
    const schema = SCHEMAS[kind];
    const result = schema.safeParse(normalized);
    if (!result.success) {
      setError(result.error.issues[0]?.message || "Invalid input");
      return;
    }
    setError("");
    await saveRecord(JSON.stringify(parsed));
  };

  const exportJson = () => {
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${kind}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 p-8">
      <div className="max-w-3xl mx-auto space-y-8">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold">IDF SDLC Console</h1>
          <p className="text-sm text-neutral-600">Operate SDLC artifacts with schema validation.</p>
        </header>

        <section className="rounded-lg border bg-white p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold">Create / Update Record</h2>
            <select
              className="border rounded px-2 py-1 text-sm bg-white"
              value={kind}
              onChange={(e) => setKind(e.target.value)}
            >
              {KINDS.map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </div>
          <form className="grid gap-3" onSubmit={onSubmit}>
            <textarea
              className="border rounded px-3 py-2 text-sm font-mono min-h-[220px]"
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
            />
            {error ? <div className="text-sm text-red-600">{error}</div> : null}
          <div>
            <Button type="submit">Save</Button>
            <Button type="button" className="ml-2 bg-neutral-700" onClick={() => setPayload(JSON.stringify(sample(kind), null, 2))}>
              Load Sample
            </Button>
            <Button type="button" className="ml-2 bg-neutral-900" onClick={exportJson}>
              Export JSON
            </Button>
          </div>
        </form>
        </section>

        <section className="rounded-lg border bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Records</h2>
            <Button className="bg-neutral-900" onClick={refresh} disabled={loading}>
              {loading ? "Loading..." : "Refresh"}
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {records.length === 0 && (
              <div className="text-sm text-neutral-600">No intents yet.</div>
            )}
            {records.map((r) => (
              <div key={r.id} className="border rounded px-3 py-2 text-sm">
                <div className="font-medium">{r.id}</div>
                <div className="text-neutral-600">{r.created_at}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

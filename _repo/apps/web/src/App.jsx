import React, { useEffect, useState } from "react";
import { useRecords } from "./store";
import { Button } from "./components/ui/button";
import { KINDS, SCHEMAS, normalize, sample } from "./schema";

export default function App() {
  const {
    kind,
    records,
    intents,
    loading,
    intentsLoading,
    setKind,
    refresh,
    refreshIntents,
    saveRecord,
  } = useRecords();
  const [payload, setPayload] = useState(JSON.stringify(sample("intent_aspirational"), null, 2));
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    refresh();
    refreshIntents();
  }, []);
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

  const copyJson = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
  };

  const openDetail = (record) => {
    setSelected(record);
    setModalOpen(true);
  };

  const parsePayload = (record) => {
    if (!record || !record.payload) return null;
    try {
      return JSON.parse(record.payload);
    } catch {
      return null;
    }
  };

  const selectedPayload = parsePayload(selected);
  const selectedCore =
    selectedPayload?.intent ||
    selectedPayload?.tension ||
    selectedPayload?.decision ||
    selectedPayload?.plugin ||
    selectedPayload?.manifest ||
    selectedPayload;
  const selectedKind =
    selectedPayload?.intent
      ? "intent"
      : selectedPayload?.tension
      ? "tension"
      : selectedPayload?.decision
      ? "decision"
      : selectedPayload?.plugin
      ? "plugin"
      : selectedPayload?.manifest
      ? "manifest"
      : selected?.kind || "record";

  return (
    <div className="min-h-screen text-neutral-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-neutral-900 text-white px-3 py-1 text-xs">
            SDLC Console
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Intent Operations Hub</h1>
          <p className="text-sm text-neutral-600">Operate SDLC artifacts with schema validation and instant inspection.</p>
        </header>

        <section className="rounded-xl border bg-white/90 backdrop-blur p-3 shadow-sm">
          <div className="flex flex-wrap items-center gap-2">
            <Button className="bg-neutral-900" onClick={refreshIntents} disabled={intentsLoading}>
              {intentsLoading ? "Loading intents..." : "Refresh intents"}
            </Button>
            <Button className="bg-neutral-900" onClick={refresh} disabled={loading}>
              {loading ? "Loading records..." : "Refresh records"}
            </Button>
            <Button className="bg-neutral-700" onClick={exportJson}>
              Export editor JSON
            </Button>
            <Button
              className="bg-neutral-700"
              onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}
              disabled={!selectedPayload}
            >
              Copy selected JSON
            </Button>
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-sm font-semibold">Create / Update Record</h2>
                <p className="text-xs text-neutral-500">JSON payload validated by schema.</p>
              </div>
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
                className="border rounded-lg px-3 py-2 text-sm font-mono min-h-[260px] bg-neutral-50/60 focus:outline-none focus:ring-2 focus:ring-neutral-300"
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

          <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Intent Index</h2>
                <p className="text-xs text-neutral-500">All intents across kinds.</p>
              </div>
              <Button className="bg-neutral-900" onClick={refreshIntents} disabled={intentsLoading}>
                {intentsLoading ? "Loading..." : "Refresh"}
              </Button>
            </div>
            <div className="mt-3 space-y-2">
              {intents.length === 0 && (
                <div className="text-sm text-neutral-600">No intents yet.</div>
              )}
              {intents.map((r) => {
                const payload = parsePayload(r);
                const core = payload?.intent || payload;
                return (
                  <button
                    key={`${r.kind}-${r.id}`}
                    className="w-full text-left border rounded-lg px-3 py-2 text-sm hover:bg-neutral-50"
                    onClick={() => openDetail(r)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{core?.id || r.id}</div>
                      <span className="text-xs text-neutral-500">{r.kind}</span>
                    </div>
                    <div className="text-neutral-600 text-xs">{core?.version || "n/a"} · {core?.status || "n/a"}</div>
                  </button>
                );
              })}
            </div>
          </section>
        </div>

        <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Records ({kind})</h2>
              <p className="text-xs text-neutral-500">All records for the selected kind.</p>
            </div>
            <Button className="bg-neutral-900" onClick={refresh} disabled={loading}>
              {loading ? "Loading..." : "Refresh"}
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {records.length === 0 && (
              <div className="text-sm text-neutral-600">No records yet.</div>
            )}
            {records.map((r) => (
              <button
                key={r.id}
                className="w-full text-left border rounded-lg px-3 py-2 text-sm hover:bg-neutral-50"
                onClick={() => openDetail(r)}
              >
                <div className="font-medium">{r.id}</div>
                <div className="text-neutral-600 text-xs">{r.created_at}</div>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Detail</h2>
              <p className="text-xs text-neutral-500">Click a record to open the modal.</p>
            </div>
          </div>
        </section>
      </div>

      {modalOpen && selected && (
        <div
          className="fixed inset-0 z-50 bg-black/40"
          onClick={() => setModalOpen(false)}
        >
          <div
            className="mx-auto mt-10 w-[min(1100px,92vw)] rounded-2xl bg-white shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b px-5 py-4 sticky top-0 bg-white rounded-t-2xl">
              <div>
                <div className="text-base font-semibold tracking-tight">{selectedCore?.id || selected.id}</div>
                <div className="text-xs text-neutral-500">{selected.kind}</div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  className="bg-neutral-700"
                  onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}
                >
                  Copy JSON
                </Button>
                <Button
                  className="bg-neutral-700"
                  onClick={() => {
                    if (!selectedPayload) return;
                    setKind(selected.kind || kind);
                    setPayload(JSON.stringify(selectedPayload, null, 2));
                    setModalOpen(false);
                  }}
                >
                  Load Into Editor
                </Button>
                <Button className="bg-neutral-900" onClick={() => setModalOpen(false)}>
                  Close
                </Button>
              </div>
            </div>
            <div className="grid gap-4 p-5 lg:grid-cols-[1.2fr_0.8fr] max-h-[72vh] overflow-hidden">
              <div className="space-y-3 overflow-auto pr-1">
                <div className="rounded-lg border bg-neutral-50 p-3 text-sm">
                  <div className="text-xs uppercase tracking-wide text-neutral-500">Summary</div>
                  <div className="mt-2 grid gap-1 text-xs text-neutral-700">
                    <div>ID: {selectedCore?.id || selected.id}</div>
                    <div>Version: {selectedCore?.version || "n/a"}</div>
                    <div>Status: {selectedCore?.status || "n/a"}</div>
                    <div>Owner: {selectedCore?.owner || "n/a"}</div>
                    <div>Priority: {selectedCore?.priority || "n/a"}</div>
                  </div>
                </div>
                {selectedCore?.declares && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Declares</div>
                    <div className="mt-2 text-sm text-neutral-700">{selectedCore.declares}</div>
                  </div>
                )}
                {selectedCore?.scope && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Scope</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      Primary: {(selectedCore.scope.primary || []).join(", ") || "n/a"}
                    </div>
                    <div className="mt-1 text-xs text-neutral-700">
                      Implicit: {(selectedCore.scope.implicit || []).join(", ") || "n/a"}
                    </div>
                  </div>
                )}
                {selectedCore?.origin && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Origin</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      {selectedCore.origin.type} · {selectedCore.origin.relationship}
                    </div>
                    <div className="text-xs text-neutral-700">Ref: {selectedCore.origin.ref}</div>
                  </div>
                )}
                {selectedCore?.current_reality && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Current Reality</div>
                    <div className="mt-2 text-xs text-neutral-700">{selectedCore.current_reality.state}</div>
                    <div className="mt-1 text-xs text-neutral-700">Status: {selectedCore.current_reality.status}</div>
                    <div className="mt-1 text-xs text-neutral-700">Remaining: {selectedCore.current_reality.remaining_work}</div>
                  </div>
                )}
                {selectedKind === "tension" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Tension</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      Between: {(selectedCore.between || [])
                        .map((b) => `${b.intent_id}@${b.version}`)
                        .join(" ↔ ") || "n/a"}
                    </div>
                    <div className="mt-1 text-xs text-neutral-700">Status: {selectedCore.status || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Created: {selectedCore.created || "n/a"}</div>
                    {selectedCore.resolution && (
                      <div className="mt-2 text-xs text-neutral-700">
                        Resolution: {selectedCore.resolution.strategy || "n/a"} · {selectedCore.resolution.resolution_owner || "n/a"}
                      </div>
                    )}
                  </div>
                )}
                {selectedKind === "decision" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Decision</div>
                    <div className="mt-2 text-xs text-neutral-700">Date: {selectedCore.date || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Status: {selectedCore.status || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">
                      Intents: {(selectedCore.intent_refs || []).join(", ") || "n/a"}
                    </div>
                  </div>
                )}
                {selectedKind === "transition" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Transition</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      {selectedCore.from_version} → {selectedCore.to_version}
                    </div>
                    <div className="mt-1 text-xs text-neutral-700">Type: {selectedCore.change_type || "n/a"}</div>
                  </div>
                )}
                {selectedKind === "plugin" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Plugin</div>
                    <div className="mt-2 text-xs text-neutral-700">Name: {selectedCore.name || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Version: {selectedCore.version || "n/a"}</div>
                  </div>
                )}
                {selectedKind === "manifest" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Manifest</div>
                    <div className="mt-2 text-xs text-neutral-700">Repo: {selectedCore.repo || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Generated: {selectedCore.generated || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Schema: {selectedCore.schema_version || "n/a"}</div>
                  </div>
                )}
              </div>
              <div className="flex flex-col min-h-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs uppercase tracking-wide text-neutral-500">JSON (secondary)</div>
                </div>
                <pre className="border rounded-lg px-3 py-2 text-xs overflow-auto bg-neutral-50 flex-1 opacity-80">
                  {JSON.stringify(selectedPayload, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

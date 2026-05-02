import React, { useEffect, useState, useCallback, useRef } from "react";
import { useRecords } from "./store";
import { Button } from "./components/ui/button";
import { KINDS, SCHEMAS, normalize, sample } from "./schema";

/* ── Helpers ── */
const KIND_LABELS = {
  intent_aspirational: "Aspirational",
  intent_achieved: "Achieved",
  tension: "Tensions",
  decision: "Decisions",
  transition: "Transitions",
  plugin: "Plugins",
  manifest: "Manifests",
};

const KIND_ICONS = {
  intent_aspirational: "\u2728",
  intent_achieved: "\u2705",
  tension: "\u26A1",
  decision: "\u2696\uFE0F",
  transition: "\u27A1\uFE0F",
  plugin: "\uD83E\uDDE9",
  manifest: "\uD83D\uDCCB",
};

const STATUS_COLORS = {
  proposed: "bg-amber-50 text-amber-700 border-amber-200",
  active: "bg-emerald-50 text-emerald-700 border-emerald-200",
  evolving: "bg-blue-50 text-blue-700 border-blue-200",
  superseded: "bg-slate-100 text-slate-500 border-slate-200",
  residual: "bg-orange-50 text-orange-600 border-orange-200",
  retracted: "bg-red-50 text-red-600 border-red-200",
  accepted: "bg-emerald-50 text-emerald-700 border-emerald-200",
  deprecated: "bg-slate-100 text-slate-500 border-slate-200",
};

const PRIORITY_COLORS = {
  critical: "bg-red-500",
  high: "bg-orange-400",
  medium: "bg-blue-400",
  low: "bg-slate-300",
};

function Badge({ children, className = "" }) {
  return (
    <span className={"inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px] font-medium leading-none " + className}>
      {children}
    </span>
  );
}

function StatusBadge({ status }) {
  if (!status) return null;
  return <Badge className={STATUS_COLORS[status] || "bg-gray-50 text-gray-600 border-gray-200"}>{status}</Badge>;
}

function PriorityDot({ priority }) {
  if (!priority) return null;
  return (
    <span className="flex items-center gap-1 text-[10px] text-[hsl(220,8%,46%)]">
      <span className={"w-1.5 h-1.5 rounded-full " + (PRIORITY_COLORS[priority] || "bg-slate-300")} />
      {priority}
    </span>
  );
}

function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center animate-fade-in">
      <div className="text-3xl mb-3 opacity-40">{icon}</div>
      <div className="text-sm font-medium text-[hsl(220,8%,46%)]">{title}</div>
      {subtitle && <div className="text-xs text-[hsl(220,8%,60%)] mt-1">{subtitle}</div>}
    </div>
  );
}

function Toast({ toast }) {
  if (!toast) return null;
  const bg = toast.type === "error" ? "bg-red-600" : "bg-emerald-600";
  return (
    <div className="fixed bottom-5 right-5 z-[100] animate-slide-up">
      <div className={bg + " text-white px-4 py-2.5 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2"}>
        <span>{toast.type === "error" ? "\u2716" : "\u2714"}</span>
        {toast.message}
      </div>
    </div>
  );
}

/* ── Main App ── */
export default function App() {
  const {
    kind, records, intents, loading, intentsLoading, toast,
    setKind, refresh, refreshIntents, saveRecord, showToast,
  } = useRecords();

  const [payload, setPayload] = useState(JSON.stringify(sample("intent_aspirational"), null, 2));
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(false);
  const [editorCollapsed, setEditorCollapsed] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    refresh();
    refreshIntents();
  }, []);

  useEffect(() => {
    refresh();
  }, [kind]);

  useEffect(() => {
    setPayload(JSON.stringify(sample(kind), null, 2));
    setError("");
  }, [kind]);

  /* Keyboard */
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape" && modalOpen) setModalOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [modalOpen]);

  const onSubmit = async (e) => {
    e.preventDefault();
    let parsed;
    try { parsed = JSON.parse(payload); } catch {
      setError("Invalid JSON \u2014 check syntax");
      return;
    }
    const normalized = normalize(kind, parsed);
    const schema = SCHEMAS[kind];
    const result = schema.safeParse(normalized);
    if (!result.success) {
      setError(result.error.issues.map(i => (i.path.length ? i.path.join(".") + ": " : "") + i.message).join("\n"));
      return;
    }
    setError("");
    setSaving(true);
    try {
      await saveRecord(JSON.stringify(parsed));
    } catch {}
    setSaving(false);
  };

  const exportJson = () => {
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = kind + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("JSON exported");
  };

  const copyJson = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast("Copied to clipboard");
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
      showToast("Copied to clipboard");
    }
  };

  const openDetail = (record) => {
    setSelected(record);
    setModalOpen(true);
  };

  const parsePayload = (record) => {
    if (!record?.payload) return null;
    try { return JSON.parse(record.payload); } catch { return null; }
  };

  /* Filters */
  const filteredRecords = records.filter((r) => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    const p = parsePayload(r);
    const core = p?.intent || p?.tension || p?.decision || p?.plugin || p?.manifest || p;
    return (
      r.id?.toLowerCase().includes(s) ||
      core?.declares?.toLowerCase().includes(s) ||
      core?.description?.toLowerCase().includes(s) ||
      core?.name?.toLowerCase().includes(s) ||
      core?.status?.toLowerCase().includes(s)
    );
  });

  const filteredIntents = intents.filter((r) => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    const p = parsePayload(r);
    const core = p?.intent || p;
    return (
      r.id?.toLowerCase().includes(s) ||
      core?.declares?.toLowerCase().includes(s) ||
      core?.status?.toLowerCase().includes(s) ||
      core?.owner?.toLowerCase().includes(s)
    );
  });

  /* Selected item */
  const selectedPayload = parsePayload(selected);
  const selectedCore = selectedPayload?.intent || selectedPayload?.tension ||
    selectedPayload?.decision || selectedPayload?.plugin ||
    selectedPayload?.manifest || selectedPayload;
  const selectedKind = selectedPayload?.intent ? "intent"
    : selectedPayload?.tension ? "tension"
    : selectedPayload?.decision ? "decision"
    : selectedPayload?.plugin ? "plugin"
    : selectedPayload?.manifest ? "manifest"
    : selected?.kind || "record";

  return (
    <div className="min-h-screen">
      {/* ── Top Bar ── */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-lg border-b border-[hsl(220,13%,91%)]">
        <div className="max-w-[1400px] mx-auto px-5 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-[hsl(220,90%,56%)] flex items-center justify-center text-white text-xs font-bold shadow-sm shadow-blue-500/25">I</div>
            <div>
              <div className="text-sm font-semibold leading-none">IDF Console</div>
              <div className="text-[10px] text-[hsl(220,8%,56%)] mt-0.5">Intent-Driven Framework</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <input
                type="text"
                placeholder="Search records..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-8 w-52 rounded-lg border border-[hsl(220,13%,88%)] bg-white pl-8 pr-3 text-xs placeholder:text-[hsl(220,8%,64%)]"
              />
              <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[hsl(220,8%,56%)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <Button variant="secondary" size="sm" onClick={() => { refresh(); refreshIntents(); }} disabled={loading || intentsLoading}>
              {loading || intentsLoading ? "\u21BB" : "\u21BB"} Sync
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto px-5 py-5">
        {/* ── Kind Tabs ── */}
        <nav className="flex items-center gap-1 mb-5 overflow-x-auto pb-1">
          {KINDS.map((k) => (
            <button
              key={k}
              data-active={kind === k}
              onClick={() => setKind(k)}
              className="kind-tab flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap"
            >
              <span>{KIND_ICONS[k]}</span>
              {KIND_LABELS[k] || k}
              {kind === k && records.length > 0 && (
                <span className="ml-0.5 bg-white/30 rounded px-1 text-[10px]">{records.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="grid gap-5 lg:grid-cols-[1fr_380px]">
          {/* ── Left Column: Editor + Records ── */}
          <div className="space-y-5">
            {/* Editor Card */}
            <section className="rounded-xl bg-white border border-[hsl(220,13%,91%)] shadow-sm overflow-hidden animate-fade-in">
              <button
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-[hsl(220,14%,98%)] transition-colors"
                onClick={() => setEditorCollapsed(!editorCollapsed)}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs">{editorCollapsed ? "\u25B6" : "\u25BC"}</span>
                  <span className="text-sm font-semibold">Create / Update</span>
                  <Badge className="bg-[hsl(220,80%,96%)] text-[hsl(220,90%,46%)] border-[hsl(220,80%,88%)]">
                    {KIND_LABELS[kind] || kind}
                  </Badge>
                </div>
                <div className="flex items-center gap-1.5">
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setPayload(JSON.stringify(sample(kind), null, 2)); }}>
                    Sample
                  </Button>
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); exportJson(); }}>
                    Export
                  </Button>
                </div>
              </button>
              {!editorCollapsed && (
                <form className="px-4 pb-4 space-y-3 animate-fade-in" onSubmit={onSubmit}>
                  <textarea
                    ref={textareaRef}
                    className="w-full border border-[hsl(220,13%,88%)] rounded-lg px-3 py-2.5 text-xs font-mono min-h-[220px] bg-[hsl(220,14%,98%)] resize-y leading-relaxed"
                    value={payload}
                    onChange={(e) => setPayload(e.target.value)}
                    spellCheck="false"
                  />
                  {error && (
                    <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700 whitespace-pre-wrap font-mono">
                      {error}
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Button type="submit" disabled={saving}>
                      {saving ? "Saving..." : "Save Record"}
                    </Button>
                  </div>
                </form>
              )}
            </section>

            {/* Records List */}
            <section className="rounded-xl bg-white border border-[hsl(220,13%,91%)] shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-[hsl(220,13%,93%)] flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold">{KIND_LABELS[kind] || kind} Records</h2>
                  <p className="text-[11px] text-[hsl(220,8%,56%)] mt-0.5">
                    {filteredRecords.length} record{filteredRecords.length !== 1 ? "s" : ""}
                    {search && " matching \u201C" + search + "\u201D"}
                  </p>
                </div>
              </div>
              <div className="divide-y divide-[hsl(220,13%,95%)] max-h-[420px] overflow-auto">
                {loading ? (
                  <div className="p-4 space-y-3">
                    {[1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}
                  </div>
                ) : filteredRecords.length === 0 ? (
                  <EmptyState
                    icon={KIND_ICONS[kind] || "\uD83D\uDCC4"}
                    title={search ? "No matching records" : "No records yet"}
                    subtitle={search ? "Try a different search term" : "Create one using the editor above"}
                  />
                ) : (
                  filteredRecords.map((r, i) => {
                    const p = parsePayload(r);
                    const core = p?.intent || p?.tension || p?.decision || p?.plugin || p?.manifest || p;
                    return (
                      <button
                        key={r.id + "-" + i}
                        className="w-full text-left px-4 py-3 hover:bg-[hsl(220,14%,98%)] transition-colors group"
                        onClick={() => openDetail(r)}
                        style={{ animationDelay: i * 30 + "ms" }}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <div className="text-sm font-medium truncate group-hover:text-[hsl(220,90%,46%)] transition-colors">
                              {core?.id || r.id}
                            </div>
                            {core?.declares && (
                              <div className="text-xs text-[hsl(220,8%,52%)] truncate mt-0.5">{core.declares}</div>
                            )}
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <PriorityDot priority={core?.priority} />
                            <StatusBadge status={core?.status} />
                          </div>
                        </div>
                        <div className="flex items-center gap-3 mt-1.5">
                          {core?.version && <span className="text-[10px] font-mono text-[hsl(220,8%,56%)]">v{core.version}</span>}
                          {core?.owner && <span className="text-[10px] text-[hsl(220,8%,56%)]">{core.owner}</span>}
                          <span className="text-[10px] text-[hsl(220,8%,64%)]">{r.created_at}</span>
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </section>
          </div>

          {/* ── Right Column: Intent Index ── */}
          <div className="space-y-5">
            <section className="rounded-xl bg-white border border-[hsl(220,13%,91%)] shadow-sm overflow-hidden lg:sticky lg:top-[76px]">
              <div className="px-4 py-3 border-b border-[hsl(220,13%,93%)] flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold">Intent Index</h2>
                  <p className="text-[11px] text-[hsl(220,8%,56%)] mt-0.5">
                    {filteredIntents.length} intent{filteredIntents.length !== 1 ? "s" : ""} across all kinds
                  </p>
                </div>
              </div>
              <div className="divide-y divide-[hsl(220,13%,95%)] max-h-[600px] overflow-auto">
                {intentsLoading ? (
                  <div className="p-4 space-y-3">
                    {[1,2,3].map(i => <div key={i} className="skeleton h-12 w-full" />)}
                  </div>
                ) : filteredIntents.length === 0 ? (
                  <EmptyState
                    icon="\u2728"
                    title="No intents yet"
                    subtitle="Create aspirational or achieved intents to see them here"
                  />
                ) : (
                  filteredIntents.map((r, i) => {
                    const p = parsePayload(r);
                    const core = p?.intent || p;
                    const isAspirational = r.kind === "intent_aspirational";
                    return (
                      <button
                        key={r.kind + "-" + r.id + "-" + i}
                        className="w-full text-left px-4 py-2.5 hover:bg-[hsl(220,14%,98%)] transition-colors group"
                        onClick={() => openDetail(r)}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="min-w-0 flex-1">
                            <div className="text-xs font-medium truncate group-hover:text-[hsl(220,90%,46%)] transition-colors">
                              {core?.id || r.id}
                            </div>
                          </div>
                          <Badge className={isAspirational ? "bg-violet-50 text-violet-600 border-violet-200" : "bg-emerald-50 text-emerald-600 border-emerald-200"}>
                            {isAspirational ? "aspirational" : "achieved"}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <StatusBadge status={core?.status} />
                          <PriorityDot priority={core?.priority} />
                          {core?.version && <span className="text-[10px] font-mono text-[hsl(220,8%,60%)]">v{core.version}</span>}
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </section>
          </div>
        </div>
      </div>

      {/* ── Modal ── */}
      {modalOpen && selected && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-fade-in flex items-start justify-center pt-[5vh] pb-8 overflow-auto"
          onClick={() => setModalOpen(false)}
        >
          <div
            className="w-[min(1100px,94vw)] rounded-2xl bg-white shadow-2xl animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[hsl(220,13%,93%)] px-6 py-4">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-semibold tracking-tight truncate">{selectedCore?.id || selected.id}</span>
                  <StatusBadge status={selectedCore?.status} />
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-[hsl(220,8%,56%)]">{selected.kind}</span>
                  {selectedCore?.version && <span className="text-xs font-mono text-[hsl(220,8%,56%)]">v{selectedCore.version}</span>}
                  <PriorityDot priority={selectedCore?.priority} />
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Button variant="secondary" size="sm" onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}>
                  Copy JSON
                </Button>
                <Button variant="secondary" size="sm" onClick={() => {
                  if (!selectedPayload) return;
                  setKind(selected.kind || kind);
                  setPayload(JSON.stringify(selectedPayload, null, 2));
                  setModalOpen(false);
                  setEditorCollapsed(false);
                }}>
                  Edit
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>
                  \u2715
                </Button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="grid gap-5 p-6 lg:grid-cols-[1.2fr_0.8fr] max-h-[74vh] overflow-hidden">
              <div className="space-y-3 overflow-auto pr-2">
                {/* Summary Card */}
                <div className="rounded-xl bg-[hsl(220,14%,98%)] border border-[hsl(220,13%,93%)] p-4">
                  <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-3">Summary</div>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs">
                    <div><span className="text-[hsl(220,8%,52%)]">ID</span><div className="font-medium font-mono mt-0.5">{selectedCore?.id || selected.id}</div></div>
                    <div><span className="text-[hsl(220,8%,52%)]">Version</span><div className="font-medium font-mono mt-0.5">{selectedCore?.version || "\u2014"}</div></div>
                    <div><span className="text-[hsl(220,8%,52%)]">Owner</span><div className="font-medium mt-0.5">{selectedCore?.owner || "\u2014"}</div></div>
                    <div><span className="text-[hsl(220,8%,52%)]">Confidence</span><div className="font-medium mt-0.5">{selectedCore?.confidence || "\u2014"}</div></div>
                  </div>
                </div>

                {selectedCore?.declares && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Declares</div>
                    <div className="text-sm text-[hsl(220,14%,20%)] leading-relaxed">{selectedCore.declares}</div>
                  </div>
                )}

                {selectedCore?.scope && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Scope</div>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {(selectedCore.scope.primary || []).map((s, i) => (
                        <Badge key={i} className="bg-[hsl(220,80%,96%)] text-[hsl(220,90%,42%)] border-[hsl(220,80%,88%)]">{s}</Badge>
                      ))}
                      {(selectedCore.scope.implicit || []).map((s, i) => (
                        <Badge key={"i-"+i} className="bg-slate-50 text-slate-500 border-slate-200">{s}</Badge>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCore?.origin && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Origin</div>
                    <div className="flex items-center gap-2 text-xs">
                      <Badge className="bg-indigo-50 text-indigo-600 border-indigo-200">{selectedCore.origin.type}</Badge>
                      <span className="text-[hsl(220,8%,52%)]">\u2192</span>
                      <Badge className="bg-slate-50 text-slate-600 border-slate-200">{selectedCore.origin.relationship}</Badge>
                    </div>
                    <div className="text-xs font-mono text-[hsl(220,8%,52%)] mt-2">ref: {selectedCore.origin.ref}</div>
                  </div>
                )}

                {selectedCore?.current_reality && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Current Reality</div>
                    <div className="space-y-1.5 text-xs">
                      <div><span className="text-[hsl(220,8%,52%)]">State:</span> <span className="font-medium">{selectedCore.current_reality.state}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Status:</span> <span className="font-medium">{selectedCore.current_reality.status}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Remaining:</span> <span className="font-medium">{selectedCore.current_reality.remaining_work}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Assessed:</span> <span className="font-mono">{selectedCore.current_reality.last_assessed}</span></div>
                    </div>
                  </div>
                )}

                {selectedKind === "tension" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Tension</div>
                    <div className="text-xs space-y-1.5">
                      <div className="flex items-center gap-2 font-mono">
                        {(selectedCore.between || []).map((b, i) => (
                          <React.Fragment key={i}>
                            {i > 0 && <span className="text-amber-500 font-bold">\u26A1</span>}
                            <Badge className="bg-amber-50 text-amber-700 border-amber-200">{b.intent_id}@{b.version}</Badge>
                          </React.Fragment>
                        ))}
                      </div>
                      <div><span className="text-[hsl(220,8%,52%)]">Created:</span> <span className="font-mono">{selectedCore.created}</span></div>
                      {selectedCore.resolution && (
                        <div className="mt-2 rounded-lg bg-[hsl(220,14%,98%)] p-2.5">
                          <div className="text-[10px] font-medium text-[hsl(220,8%,52%)] mb-1">Resolution</div>
                          <div>{selectedCore.resolution.strategy} \u00B7 {selectedCore.resolution.resolution_owner}</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {selectedKind === "decision" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Decision</div>
                    <div className="text-xs space-y-1.5">
                      <div><span className="text-[hsl(220,8%,52%)]">Date:</span> <span className="font-mono">{selectedCore.date}</span></div>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-[hsl(220,8%,52%)]">Refs:</span>
                        {(selectedCore.intent_refs || []).map((ref, i) => (
                          <Badge key={i} className="bg-blue-50 text-blue-600 border-blue-200">{ref}</Badge>
                        ))}
                      </div>
                      {selectedCore.context && <div className="mt-2 text-[hsl(220,14%,20%)]"><span className="text-[hsl(220,8%,52%)]">Context:</span> {selectedCore.context}</div>}
                      {selectedCore.consequences && <div className="text-[hsl(220,14%,20%)]"><span className="text-[hsl(220,8%,52%)]">Consequences:</span> {selectedCore.consequences}</div>}
                    </div>
                  </div>
                )}

                {selectedKind === "transition" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Transition</div>
                    <div className="flex items-center gap-2 text-xs font-mono">
                      <Badge className="bg-slate-100 text-slate-600 border-slate-200">{selectedCore.from_version}</Badge>
                      <span className="text-[hsl(220,90%,56%)] font-bold">\u2192</span>
                      <Badge className="bg-emerald-50 text-emerald-600 border-emerald-200">{selectedCore.to_version}</Badge>
                    </div>
                    <div className="text-xs mt-2"><span className="text-[hsl(220,8%,52%)]">Type:</span> <Badge className="bg-blue-50 text-blue-600 border-blue-200">{selectedCore.change_type}</Badge></div>
                  </div>
                )}

                {selectedKind === "plugin" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Plugin</div>
                    <div className="text-xs space-y-1.5">
                      <div className="font-medium text-sm">{selectedCore.name}</div>
                      <div className="font-mono text-[hsl(220,8%,52%)]">v{selectedCore.version}</div>
                      {selectedCore.description && <div className="text-[hsl(220,14%,20%)]">{selectedCore.description}</div>}
                    </div>
                  </div>
                )}

                {selectedKind === "manifest" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Manifest</div>
                    <div className="text-xs space-y-1.5">
                      <div><span className="text-[hsl(220,8%,52%)]">Repo:</span> <span className="font-mono font-medium">{selectedCore.repo}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Generated:</span> <span className="font-mono">{selectedCore.generated}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Schema:</span> <span className="font-mono">{selectedCore.schema_version}</span></div>
                    </div>
                  </div>
                )}
              </div>

              {/* JSON Pane */}
              <div className="flex flex-col min-h-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium">Raw JSON</div>
                  <Button variant="ghost" size="sm" onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}>
                    Copy
                  </Button>
                </div>
                <pre className="border border-[hsl(220,13%,91%)] rounded-xl px-4 py-3 text-[11px] font-mono overflow-auto bg-[hsl(220,14%,98%)] flex-1 leading-relaxed text-[hsl(220,14%,30%)]">
                  {JSON.stringify(selectedPayload, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      <Toast toast={toast} />
    </div>
  );
}

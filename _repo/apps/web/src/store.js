import { create } from "zustand";
import { listRecords, upsertRecord } from "./lib/api";

export const useRecords = create((set, get) => ({
  kind: "intent_aspirational",
  records: [],
  intents: [],
  loading: false,
  intentsLoading: false,
  setKind(kind) {
    set({ kind });
  },
  async refresh() {
    const kind = get().kind;
    set({ loading: true });
    const records = await listRecords(kind);
    set({ records, loading: false });
  },
  async refreshIntents() {
    set({ intentsLoading: true });
    const [asp, ach] = await Promise.all([
      listRecords("intent_aspirational"),
      listRecords("intent_achieved"),
    ]);
    const merged = [...asp, ...ach].map((r) => ({
      ...r,
      kind: r.kind || (asp.includes(r) ? "intent_aspirational" : "intent_achieved"),
    }));
    set({ intents: merged, intentsLoading: false });
  },
  async saveRecord(payload) {
    const kind = get().kind;
    const saved = await upsertRecord(kind, payload);
    set({ records: [saved, ...get().records.filter(r => r.id !== saved.id)] });
    if (kind === "intent_aspirational" || kind === "intent_achieved") {
      set({ intents: [saved, ...get().intents.filter(r => r.id !== saved.id)] });
    }
  }
}));

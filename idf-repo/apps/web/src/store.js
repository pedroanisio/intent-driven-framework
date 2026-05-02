import { create } from "zustand";
import { listRecords, upsertRecord } from "./lib/api";

export const useRecords = create((set, get) => ({
  kind: "intent_aspirational",
  records: [],
  intents: [],
  loading: false,
  intentsLoading: false,
  toast: null,
  setKind(kind) {
    set({ kind });
  },
  showToast(message, type = "success") {
    set({ toast: { message, type, id: Date.now() } });
    setTimeout(() => set({ toast: null }), 3000);
  },
  async refresh() {
    const kind = get().kind;
    set({ loading: true });
    try {
      const records = await listRecords(kind);
      set({ records, loading: false });
    } catch (err) {
      set({ loading: false });
      get().showToast("Failed to load records: " + err.message, "error");
    }
  },
  async refreshIntents() {
    set({ intentsLoading: true });
    try {
      const [asp, ach] = await Promise.all([
        listRecords("intent_aspirational"),
        listRecords("intent_achieved"),
      ]);
      const merged = [...asp, ...ach].map((r) => ({
        ...r,
        kind: r.kind || (asp.includes(r) ? "intent_aspirational" : "intent_achieved"),
      }));
      set({ intents: merged, intentsLoading: false });
    } catch (err) {
      set({ intentsLoading: false });
      get().showToast("Failed to load intents: " + err.message, "error");
    }
  },
  async saveRecord(payload) {
    const kind = get().kind;
    try {
      const saved = await upsertRecord(kind, payload);
      set({ records: [saved, ...get().records.filter(r => r.id !== saved.id)] });
      if (kind === "intent_aspirational" || kind === "intent_achieved") {
        set({ intents: [saved, ...get().intents.filter(r => r.id !== saved.id)] });
      }
      get().showToast("Record saved successfully", "success");
      return saved;
    } catch (err) {
      get().showToast("Save failed: " + err.message, "error");
      throw err;
    }
  }
}));

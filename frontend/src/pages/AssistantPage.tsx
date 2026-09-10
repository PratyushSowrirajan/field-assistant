import { useEffect, useRef, useState } from "react";
import { useAllFields, useAskAssistant, useFarms } from "@/lib/queries";
import type { ChatTurn } from "@/types/api";

interface Message extends ChatTurn {
  id: string;
  sources?: string[];
  error?: boolean;
}

const SUGGESTIONS = [
  "Is my field okay right now?",
  "Should I irrigate today?",
  "What's the biggest risk in my field?",
  "What should I do about the latest alert?",
];

export default function AssistantPage() {
  const { data: farms } = useFarms();
  const { data: allFields } = useAllFields(farms);
  const fields = (allFields ?? []).filter((f) => !f.archived);
  const [fieldId, setFieldId] = useState<string>("");

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const ask = useAskAssistant();
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, ask.isPending]);

  async function send(question: string) {
    const q = question.trim();
    if (!q || ask.isPending) return;

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: q };
    const history: ChatTurn[] = [...messages, userMsg].map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await ask.mutateAsync({ question: q, fieldId: fieldId || undefined, history: history.slice(0, -1) });
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Something went wrong. Please try again.";
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "assistant", content: detail, error: true }]);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-140px)] max-w-2xl flex-col">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-bold text-forest">Assistant</h1>
          <p className="text-sm text-ink/60">Ask about your fields, alerts, or what to do next.</p>
        </div>
        {fields.length > 0 && (
          <select value={fieldId} onChange={(e) => setFieldId(e.target.value)} className="input w-auto">
            <option value="">All fields</option>
            {fields.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
        )}
      </div>

      <div ref={listRef} className="card flex-1 space-y-3 overflow-y-auto">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-4 py-6 text-center">
            <p className="text-sm text-ink/60">Ask anything about what's happening in your fields.</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-sand bg-sand/40 px-3 py-1.5 text-xs font-medium text-ink/70 hover:bg-sand"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-xl2 px-4 py-2.5 text-sm ${
                m.role === "user"
                  ? "bg-forest text-cream"
                  : m.error
                    ? "bg-risk-critical/10 text-risk-critical"
                    : "bg-sand/60 text-ink"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.sources && m.sources.length > 0 && (
                <p className="mt-1.5 text-[11px] text-ink/40">Based on: {m.sources.join(", ")}</p>
              )}
            </div>
          </div>
        ))}

        {ask.isPending && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-xl2 bg-sand/60 px-4 py-2.5 text-sm text-ink/50">Thinking...</div>
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="mt-3 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          className="input flex-1"
          maxLength={500}
        />
        <button type="submit" disabled={ask.isPending || !input.trim()} className="btn-primary px-5">
          Send
        </button>
      </form>
    </div>
  );
}

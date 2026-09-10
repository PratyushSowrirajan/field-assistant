import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAllFields, useAskAssistant, useFarms } from "@/lib/queries";
import type { ChatTurn } from "@/types/api";

interface Message extends ChatTurn {
  id: string;
  sources?: string[];
  error?: boolean;
}

const SUGGESTION_KEYS = ["assistant.suggestion1", "assistant.suggestion2", "assistant.suggestion3", "assistant.suggestion4"];

export default function AssistantWidget() {
  const { t } = useTranslation();
  const { data: farms } = useFarms();
  const { data: allFields } = useAllFields(farms);
  const fields = (allFields ?? []).filter((f) => !f.archived);
  const [fieldId, setFieldId] = useState<string>("");

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const ask = useAskAssistant();
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, ask.isPending]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

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
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
      {open && (
        <div
          role="dialog"
          aria-label={t("assistant.title")}
          className="animate-pop-in flex h-[min(600px,calc(100vh-7.5rem))] w-[calc(100vw-2.5rem)] max-w-sm flex-col overflow-hidden rounded-2xl border border-sand bg-cream shadow-2xl sm:w-96"
        >
          {/* Header */}
          <div className="flex items-center justify-between gap-2 bg-forest px-4 py-3 text-cream">
            <div className="flex min-w-0 items-center gap-2.5">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-leaf/25">
                <SproutIcon className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold leading-tight">{t("assistant.title")}</p>
                <p className="truncate text-[11px] leading-tight text-cream/70">{t("assistant.subtitle")}</p>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label={t("assistant.closeLabel")}
              className="shrink-0 rounded-full p-1.5 text-cream/80 hover:bg-white/10 hover:text-cream"
            >
              <CloseIcon className="h-4 w-4" />
            </button>
          </div>

          {fields.length > 0 && (
            <div className="border-b border-sand bg-sand/30 px-3 py-1.5">
              <select
                value={fieldId}
                onChange={(e) => setFieldId(e.target.value)}
                className="w-full bg-transparent text-xs font-medium text-ink/60 focus:outline-none"
              >
                <option value="">{t("assistant.allFields")}</option>
                {fields.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Messages */}
          <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-3 py-3">
            {messages.length === 0 && (
              <div className="flex h-full flex-col items-center justify-center gap-4 px-2 py-4 text-center">
                <div className="flex h-11 w-11 items-center justify-center rounded-full bg-leaf/15 text-leaf-dark">
                  <SproutIcon className="h-5 w-5" />
                </div>
                <p className="text-sm text-ink/60">{t("assistant.emptyPrompt")}</p>
                <div className="flex flex-wrap justify-center gap-1.5">
                  {SUGGESTION_KEYS.map((key) => (
                    <button
                      key={key}
                      onClick={() => send(t(key))}
                      className="rounded-full border border-sand bg-white px-2.5 py-1 text-[11px] font-medium text-ink/70 hover:border-leaf hover:bg-leaf/10"
                    >
                      {t(key)}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((m) => (
              <div key={m.id} className={`animate-bubble-in flex items-end gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                {m.role === "assistant" && (
                  <div className="mb-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-leaf/15 text-leaf-dark">
                    <SproutIcon className="h-3.5 w-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-3.5 py-2 text-sm leading-snug shadow-sm ${
                    m.role === "user"
                      ? "rounded-br-md bg-forest text-cream"
                      : m.error
                        ? "rounded-bl-md bg-risk-critical/10 text-risk-critical"
                        : "rounded-bl-md border border-sand bg-white text-ink"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.content}</p>
                  {m.sources && m.sources.length > 0 && (
                    <p className="mt-1.5 text-[10px] text-ink/40">{t("assistant.basedOn", { sources: m.sources.join(", ") })}</p>
                  )}
                </div>
              </div>
            ))}

            {ask.isPending && (
              <div className="flex items-end gap-2">
                <div className="mb-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-leaf/15 text-leaf-dark">
                  <SproutIcon className="h-3.5 w-3.5" />
                </div>
                <div className="rounded-2xl rounded-bl-md border border-sand bg-white px-3.5 py-2.5 shadow-sm">
                  <TypingDots />
                </div>
              </div>
            )}
          </div>

          {/* Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex items-center gap-2 border-t border-sand bg-white px-2.5 py-2.5"
          >
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("assistant.placeholder")}
              className="flex-1 rounded-full border border-sand bg-cream px-3.5 py-2 text-sm text-ink placeholder:text-ink/40 focus:border-leaf focus:outline-none focus:ring-2 focus:ring-leaf/30"
              maxLength={500}
            />
            <button
              type="submit"
              disabled={ask.isPending || !input.trim()}
              aria-label={t("assistant.send")}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-forest text-cream transition-colors hover:bg-forest-light disabled:cursor-not-allowed disabled:opacity-40"
            >
              <SendIcon className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}

      {/* Floating launcher */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? t("assistant.closeLabel") : t("assistant.openLabel")}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-forest text-cream shadow-lg transition-transform hover:scale-105 hover:bg-forest-light active:scale-95"
      >
        {open ? <CloseIcon className="h-6 w-6" /> : <ChatIcon className="h-6 w-6" />}
      </button>
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-0.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink/30"
          style={{ animationDelay: `${i * 0.15}s`, animationDuration: "0.9s" }}
        />
      ))}
    </div>
  );
}

function SproutIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M5 19c8 0 14-6 14-14 0 0-12-1-14 8-1 4 0 6 0 6Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M5 19c0-4 2-8 6-10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function ChatIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M4 12a8 8 0 1 1 3.2 6.4L4 20l1.1-3.6A7.96 7.96 0 0 1 4 12Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function SendIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M4 12l16-7-6 16-2.5-6.5L4 12Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

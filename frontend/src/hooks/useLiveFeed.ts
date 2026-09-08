import { useEffect, useRef, useState } from "react";
import { WS_BASE_URL, getToken } from "@/lib/api";
import type { RoverLiveState } from "@/types/api";

type LiveMessage = { type: "rover_telemetry"; data: RoverLiveState & { last_update_at: string } };

/** Subscribes to the farmer's live rover feed over WebSocket. Falls back gracefully
 * if the connection drops — callers should still poll REST for the initial/backup state. */
export function useLiveFeed() {
  const [lastMessage, setLastMessage] = useState<LiveMessage["data"] | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    let cancelled = false;
    let retryTimer: number | undefined;

    function connect() {
      const ws = new WebSocket(`${WS_BASE_URL}/ws/live?token=${encodeURIComponent(token!)}`);
      wsRef.current = ws;

      ws.onopen = () => !cancelled && setConnected(true);
      ws.onclose = () => {
        if (cancelled) return;
        setConnected(false);
        retryTimer = window.setTimeout(connect, 4000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (event) => {
        try {
          const msg: LiveMessage = JSON.parse(event.data);
          if (msg.type === "rover_telemetry") setLastMessage(msg.data);
        } catch {
          /* ignore malformed frames */
        }
      };
    }

    connect();
    return () => {
      cancelled = true;
      window.clearTimeout(retryTimer);
      wsRef.current?.close();
    };
  }, []);

  return { lastMessage, connected };
}

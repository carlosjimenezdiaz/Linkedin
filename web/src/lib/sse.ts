/**
 * lib/sse.ts — SSE hook for pipeline progress streaming.
 */
import { useEffect, useRef, useState, useCallback } from "react";
import { getPipelineStreamURL } from "./api";

export interface SSEEvent {
  event: "progress" | "complete" | "error";
  data: {
    phase?: string;
    message?: string;
    pct?: number;
    post_id?: string;
    brief_id?: string;
  };
}

export function useSSE(runId: string | null) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestEvent, setLatestEvent] = useState<SSEEvent | null>(null);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!runId) return;

    setEvents([]);
    setIsComplete(false);
    setError(null);

    const url = getPipelineStreamURL(runId);
    const source = new EventSource(url);
    sourceRef.current = source;

    const handleEvent = (type: SSEEvent["event"]) => (e: MessageEvent) => {
      const data = JSON.parse(e.data);
      const evt: SSEEvent = { event: type, data };
      setEvents((prev) => [...prev, evt]);
      setLatestEvent(evt);

      if (type === "complete") {
        setIsComplete(true);
        source.close();
      }
      if (type === "error") {
        setError(data.message);
        source.close();
      }
    };

    source.addEventListener("progress", handleEvent("progress"));
    source.addEventListener("complete", handleEvent("complete"));
    source.addEventListener("error", handleEvent("error"));

    // Native EventSource error (connection lost)
    source.onerror = () => {
      if (!isComplete) {
        setError("Connection lost");
        source.close();
      }
    };

    return () => {
      source.close();
    };
  }, [runId]);

  const reset = useCallback(() => {
    setEvents([]);
    setIsComplete(false);
    setError(null);
    setLatestEvent(null);
  }, []);

  return { events, latestEvent, isComplete, error, reset };
}

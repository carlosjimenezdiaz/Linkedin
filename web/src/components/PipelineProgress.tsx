"use client";

import { useSSE } from "@/lib/sse";

const PHASES = ["research", "write", "image"];

export function PipelineProgress({
  runId,
  onComplete,
}: {
  runId: string | null;
  onComplete?: (postId: string | undefined) => void;
}) {
  const { latestEvent, isComplete, error } = useSSE(runId);

  const phase = latestEvent?.data?.phase || "starting";
  const message = latestEvent?.data?.message || "Initializing...";
  const pct = latestEvent?.data?.pct || 0;

  // Notify parent when complete
  if (isComplete && onComplete && latestEvent?.data?.post_id) {
    onComplete(latestEvent.data.post_id);
  }

  if (!runId) return null;

  return (
    <div
      className="rounded-lg p-6 space-y-4"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      {/* Phase stepper */}
      <div className="flex gap-4 items-center">
        {PHASES.map((p) => {
          const isCurrent = phase === p;
          const isDone =
            isComplete || PHASES.indexOf(p) < PHASES.indexOf(phase);
          return (
            <div key={p} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{
                  background: isDone
                    ? "var(--accent)"
                    : isCurrent
                    ? "var(--accent)"
                    : "var(--border)",
                  opacity: isDone ? 1 : isCurrent ? 0.8 : 0.4,
                }}
              />
              <span
                className="text-sm capitalize"
                style={{
                  color: isCurrent || isDone ? "var(--foreground)" : "var(--muted)",
                  fontWeight: isCurrent ? 600 : 400,
                }}
              >
                {p}
              </span>
            </div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 rounded-full" style={{ background: "var(--border)" }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: "var(--accent)" }}
        />
      </div>

      {/* Status message */}
      <p className="text-sm" style={{ color: "var(--muted)" }}>
        {error ? (
          <span style={{ color: "var(--pillar-risk)" }}>Error: {error}</span>
        ) : isComplete ? (
          <span style={{ color: "var(--pillar-wealth)" }}>Complete!</span>
        ) : (
          message
        )}
      </p>
    </div>
  );
}

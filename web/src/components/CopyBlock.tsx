"use client";

import { useState } from "react";

export function CopyBlock({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <button
        onClick={handleCopy}
        className="absolute top-3 right-3 px-3 py-1 rounded text-xs font-medium transition-colors"
        style={{
          background: copied ? "var(--pillar-wealth)" : "var(--accent)",
          color: "var(--background)",
        }}
      >
        {copied ? "Copied!" : "Copy"}
      </button>
      <pre
        className="p-4 rounded-lg text-sm whitespace-pre-wrap overflow-x-auto"
        style={{ background: "var(--background)", border: "1px solid var(--border)" }}
      >
        {text}
      </pre>
    </div>
  );
}

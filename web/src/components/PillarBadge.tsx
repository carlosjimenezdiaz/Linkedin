"use client";

const PILLAR_COLORS: Record<string, string> = {
  "agentic-ai": "var(--pillar-agentic)",
  "traditional-ml": "var(--pillar-ml)",
  "wealth-asset-management": "var(--pillar-wealth)",
  "risk-management": "var(--pillar-risk)",
  general: "var(--muted)",
};

const PILLAR_LABELS: Record<string, string> = {
  "agentic-ai": "Agentic AI",
  "traditional-ml": "Traditional ML",
  "wealth-asset-management": "Wealth & AM",
  "risk-management": "Risk Mgmt",
  general: "General",
};

export function PillarBadge({ pillar }: { pillar: string }) {
  const color = PILLAR_COLORS[pillar] || PILLAR_COLORS.general;
  const label = PILLAR_LABELS[pillar] || pillar;

  return (
    <span
      className="inline-block px-2 py-0.5 rounded text-xs font-medium"
      style={{ background: color, color: "var(--background)" }}
    >
      {label}
    </span>
  );
}

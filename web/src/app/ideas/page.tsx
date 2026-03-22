"use client";

import { useEffect, useState } from "react";
import { listIdeas, updateIdea, migrateIdeas, type Idea } from "@/lib/api";
import { PillarBadge } from "@/components/PillarBadge";

export default function IdeasPage() {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("");
  const [migrating, setMigrating] = useState(false);

  useEffect(() => {
    loadIdeas();
  }, [filter]);

  const loadIdeas = async () => {
    setLoading(true);
    try {
      const data = await listIdeas(filter || undefined);
      setIdeas(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleMigrate = async () => {
    setMigrating(true);
    try {
      const result = await migrateIdeas();
      alert(`Migrated ${result.migrated} ideas from ideas.md`);
      loadIdeas();
    } catch (err) {
      console.error(err);
      alert("Migration failed — check console");
    } finally {
      setMigrating(false);
    }
  };

  const STATUS_COLORS: Record<string, string> = {
    backlog: "var(--border)",
    "in-progress": "var(--pillar-agentic)",
    drafted: "var(--accent)",
    published: "var(--pillar-wealth)",
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
            Ideas Backlog
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
            {ideas.length} ideas total
          </p>
        </div>
        <button
          onClick={handleMigrate}
          disabled={migrating}
          className="px-3 py-1.5 rounded text-xs font-medium"
          style={{ background: "var(--border)", color: "var(--foreground)" }}
        >
          {migrating ? "Migrating..." : "Import from ideas.md"}
        </button>
      </div>

      {/* Filter */}
      <select
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="px-3 py-1.5 rounded-md text-sm"
        style={{ background: "var(--card)", border: "1px solid var(--border)", color: "var(--foreground)" }}
      >
        <option value="">All statuses</option>
        <option value="backlog">Backlog</option>
        <option value="in-progress">In Progress</option>
        <option value="drafted">Drafted</option>
        <option value="published">Published</option>
      </select>

      {loading ? (
        <p style={{ color: "var(--muted)" }}>Loading...</p>
      ) : ideas.length === 0 ? (
        <div
          className="p-6 rounded-lg text-center"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <p className="text-sm" style={{ color: "var(--muted)" }}>
            No ideas yet. Click &quot;Import from ideas.md&quot; to migrate existing ideas,
            or create posts from the Create page.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {ideas.map((idea) => (
            <div
              key={idea.id}
              className="flex items-center gap-4 p-3 rounded-lg"
              style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
              <span
                className="text-xs font-mono w-10 text-center"
                style={{ color: "var(--muted)" }}
              >
                #{String(idea.number).padStart(3, "0")}
              </span>

              {idea.pillar && <PillarBadge pillar={idea.pillar} />}

              <span className="flex-1 text-sm">{idea.title}</span>

              <span className="text-xs" style={{ color: "var(--muted)" }}>
                {idea.post_type}
              </span>

              <select
                value={idea.status}
                onChange={async (e) => {
                  await updateIdea(idea.id, { status: e.target.value });
                  loadIdeas();
                }}
                className="px-2 py-1 rounded text-xs"
                style={{
                  background: STATUS_COLORS[idea.status] || "var(--border)",
                  color: idea.status === "backlog" ? "var(--muted)" : "var(--background)",
                  border: "none",
                }}
              >
                <option value="backlog">backlog</option>
                <option value="in-progress">in-progress</option>
                <option value="drafted">drafted</option>
                <option value="published">published</option>
              </select>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

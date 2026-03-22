"use client";

import { useEffect, useState } from "react";
import { listInfluencers, addInfluencer, deleteInfluencer, type Influencer } from "@/lib/api";
import { PillarBadge } from "@/components/PillarBadge";

export default function InfluencersPage() {
  const [influencers, setInfluencers] = useState<Influencer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [newPillar, setNewPillar] = useState("agentic-ai");
  const [newNote, setNewNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadInfluencers();
  }, []);

  const loadInfluencers = async () => {
    setLoading(true);
    try {
      const data = await listInfluencers();
      setInfluencers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newUrl.trim()) return;
    setSubmitting(true);
    try {
      await addInfluencer({
        name: newName.trim(),
        url: newUrl.trim(),
        pillar: newPillar,
        note: newNote.trim() || undefined,
      });
      setNewName("");
      setNewUrl("");
      setNewPillar("agentic-ai");
      setNewNote("");
      setShowAdd(false);
      loadInfluencers();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Remove ${name} from influencers?`)) return;
    try {
      await deleteInfluencer(name);
      loadInfluencers();
    } catch (err) {
      console.error(err);
    }
  };

  const PILLARS = [
    "agentic-ai",
    "traditional-ml",
    "wealth-asset-management",
    "risk-management",
    "ai-in-finance",
    "ai-governance-risk",
  ];

  const inputStyle = {
    background: "var(--background)",
    border: "1px solid var(--border)",
    color: "var(--foreground)",
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
            Influencers
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
            LinkedIn profiles tracked for content research
          </p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="px-3 py-1.5 rounded text-xs font-medium"
          style={{ background: "var(--accent)", color: "var(--background)" }}
        >
          {showAdd ? "Cancel" : "+ Add Influencer"}
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <form
          onSubmit={handleAdd}
          className="p-4 rounded-lg space-y-3"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs mb-1" style={{ color: "var(--muted)" }}>Name</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Full name"
                className="w-full px-2 py-1.5 rounded text-sm"
                style={inputStyle}
                required
              />
            </div>
            <div>
              <label className="block text-xs mb-1" style={{ color: "var(--muted)" }}>LinkedIn URL</label>
              <input
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://www.linkedin.com/in/..."
                className="w-full px-2 py-1.5 rounded text-sm"
                style={inputStyle}
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs mb-1" style={{ color: "var(--muted)" }}>Pillar</label>
              <select
                value={newPillar}
                onChange={(e) => setNewPillar(e.target.value)}
                className="w-full px-2 py-1.5 rounded text-sm"
                style={inputStyle}
              >
                {PILLARS.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs mb-1" style={{ color: "var(--muted)" }}>Note (optional)</label>
              <input
                type="text"
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Why follow this person?"
                className="w-full px-2 py-1.5 rounded text-sm"
                style={inputStyle}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-1.5 rounded text-xs font-medium disabled:opacity-50"
            style={{ background: "var(--accent)", color: "var(--background)" }}
          >
            {submitting ? "Adding..." : "Add"}
          </button>
        </form>
      )}

      {/* Influencer list */}
      {loading ? (
        <p style={{ color: "var(--muted)" }}>Loading...</p>
      ) : influencers.length === 0 ? (
        <div
          className="p-6 rounded-lg text-center"
          style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        >
          <p className="text-sm" style={{ color: "var(--muted)" }}>
            No influencers configured. Add one above.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {influencers.map((inf) => (
            <div
              key={inf.name}
              className="flex items-center gap-4 p-4 rounded-lg"
              style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{inf.name}</span>
                  <PillarBadge pillar={inf.pillar} />
                </div>
                <a
                  href={inf.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs hover:underline block mt-0.5"
                  style={{ color: "var(--accent)" }}
                >
                  {inf.url}
                </a>
                {inf.note && (
                  <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
                    {inf.note}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleDelete(inf.name)}
                className="px-2 py-1 rounded text-xs"
                style={{ color: "var(--pillar-risk)" }}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { startFullPipeline, startResearch, listIdeas, type Idea } from "@/lib/api";
import { PipelineProgress } from "@/components/PipelineProgress";
import { PillarBadge } from "@/components/PillarBadge";

const POST_TYPES = [
  { value: "thought-leadership", label: "Thought Leadership" },
  { value: "story", label: "Story" },
  { value: "news", label: "News Commentary" },
  { value: "cta", label: "CTA" },
];

const IMAGE_TYPES = [
  { value: "auto", label: "Auto (inferred)" },
  { value: "diagram", label: "Diagram" },
  { value: "branded", label: "Branded" },
  { value: "infographic", label: "Infographic" },
  { value: "carousel", label: "Carousel" },
  { value: "none", label: "No image" },
];

export default function CreatePage() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [postType, setPostType] = useState("thought-leadership");
  const [imageType, setImageType] = useState("auto");
  const [researchOnly, setResearchOnly] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [selectedIdeaId, setSelectedIdeaId] = useState<string | null>(null);
  const [showIdeas, setShowIdeas] = useState(false);
  const [ideaFilter, setIdeaFilter] = useState("");

  useEffect(() => {
    listIdeas("backlog").then(setIdeas).catch(console.error);
  }, []);

  const filteredIdeas = ideas.filter((idea) =>
    idea.title.toLowerCase().includes(ideaFilter.toLowerCase())
  );

  const handleIdeaSelect = (idea: Idea) => {
    setTopic(idea.title);
    setSelectedIdeaId(idea.id);
    if (idea.post_type) setPostType(idea.post_type);
    setShowIdeas(false);
    setIdeaFilter("");
  };

  const handleTopicChange = (value: string) => {
    setTopic(value);
    setSelectedIdeaId(null);
    if (value.length > 0 && !showIdeas) setShowIdeas(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setSubmitting(true);
    try {
      const fn = researchOnly ? startResearch : startFullPipeline;
      const result = await fn({
        topic: topic.trim(),
        post_type: postType,
        image_type: imageType,
        idea_id: selectedIdeaId || undefined,
      });
      setRunId(result.run_id);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleComplete = (postId: string | undefined) => {
    if (postId) {
      setTimeout(() => router.push(`/posts?id=${postId}`), 1500);
    }
  };

  const inputStyle = {
    background: "var(--background)",
    border: "1px solid var(--border)",
    color: "var(--foreground)",
  };

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
          Create Post
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
          Run the full pipeline: research, write, generate image
        </p>
      </div>

      {!runId ? (
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Topic with idea suggestions */}
          <div className="relative">
            <label className="block text-sm font-medium mb-1">Topic</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => handleTopicChange(e.target.value)}
              onFocus={() => setShowIdeas(true)}
              placeholder='Type your own topic or pick from ideas below...'
              className="w-full px-3 py-2 rounded-md text-sm"
              style={inputStyle}
              required
            />
            {selectedIdeaId && (
              <span
                className="absolute right-3 top-[34px] text-xs px-2 py-0.5 rounded"
                style={{ background: "var(--pillar-wealth)", color: "var(--background)" }}
              >
                From backlog
              </span>
            )}

            {/* Ideas dropdown */}
            {showIdeas && ideas.length > 0 && (
              <div
                className="absolute z-10 w-full mt-1 rounded-lg shadow-lg max-h-64 overflow-y-auto"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
              >
                <div className="sticky top-0 p-2" style={{ background: "var(--card)" }}>
                  <input
                    type="text"
                    value={ideaFilter}
                    onChange={(e) => setIdeaFilter(e.target.value)}
                    placeholder="Filter ideas..."
                    className="w-full px-2 py-1 rounded text-xs"
                    style={inputStyle}
                  />
                </div>
                {filteredIdeas.map((idea) => (
                  <button
                    key={idea.id}
                    type="button"
                    onClick={() => handleIdeaSelect(idea)}
                    className="w-full text-left px-3 py-2 text-sm hover:opacity-80 flex items-center gap-2"
                    style={{ borderBottom: "1px solid var(--border)" }}
                  >
                    <span className="text-xs font-mono" style={{ color: "var(--muted)" }}>
                      #{String(idea.number).padStart(3, "0")}
                    </span>
                    {idea.pillar && <PillarBadge pillar={idea.pillar} />}
                    <span className="flex-1 truncate">{idea.title}</span>
                    <span className="text-xs" style={{ color: "var(--muted)" }}>
                      {idea.post_type}
                    </span>
                  </button>
                ))}
                {filteredIdeas.length === 0 && (
                  <p className="px-3 py-2 text-xs" style={{ color: "var(--muted)" }}>
                    No matching ideas — type your own topic above
                  </p>
                )}
                <button
                  type="button"
                  onClick={() => { setShowIdeas(false); setIdeaFilter(""); }}
                  className="w-full text-center py-2 text-xs"
                  style={{ color: "var(--muted)" }}
                >
                  Close
                </button>
              </div>
            )}
          </div>

          {/* Post Type */}
          <div>
            <label className="block text-sm font-medium mb-1">Post Type</label>
            <select
              value={postType}
              onChange={(e) => setPostType(e.target.value)}
              className="w-full px-3 py-2 rounded-md text-sm"
              style={inputStyle}
            >
              {POST_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* Image Type */}
          <div>
            <label className="block text-sm font-medium mb-1">Image Type</label>
            <select
              value={imageType}
              onChange={(e) => setImageType(e.target.value)}
              className="w-full px-3 py-2 rounded-md text-sm"
              style={inputStyle}
              disabled={researchOnly}
            >
              {IMAGE_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* Research only toggle */}
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={researchOnly}
              onChange={(e) => setResearchOnly(e.target.checked)}
              className="rounded"
            />
            Research only (skip writing and images)
          </label>

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting || !topic.trim()}
            className="px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            style={{ background: "var(--accent)", color: "var(--background)" }}
          >
            {submitting ? "Starting..." : researchOnly ? "Start Research" : "Generate Post"}
          </button>
        </form>
      ) : (
        <PipelineProgress runId={runId} onComplete={handleComplete} />
      )}
    </div>
  );
}

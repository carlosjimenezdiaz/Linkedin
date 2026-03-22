"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { listPosts, getPost, updatePost, deletePost, type Post } from "@/lib/api";
import { PillarBadge } from "@/components/PillarBadge";
import { CopyBlock } from "@/components/CopyBlock";

export default function PostsPage() {
  return (
    <Suspense fallback={<p style={{ color: "var(--muted)" }}>Loading...</p>}>
      <PostsContent />
    </Suspense>
  );
}

function PostsContent() {
  const searchParams = useSearchParams();
  const selectedId = searchParams.get("id");

  const [posts, setPosts] = useState<Post[]>([]);
  const [selected, setSelected] = useState<Post | null>(null);
  const [filter, setFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editBody, setEditBody] = useState("");
  const [scheduledDate, setScheduledDate] = useState("");
  const [scheduledTime, setScheduledTime] = useState("");

  useEffect(() => {
    loadPosts();
  }, [filter]);

  useEffect(() => {
    if (selectedId) {
      getPost(selectedId).then((p) => {
        setSelected(p);
        loadSchedule(p);
      }).catch(console.error);
    }
  }, [selectedId]);

  const loadSchedule = (post: Post) => {
    if (post.scheduled_at) {
      const dt = new Date(post.scheduled_at);
      setScheduledDate(dt.toISOString().slice(0, 10));
      setScheduledTime(dt.toISOString().slice(11, 16));
    } else {
      setScheduledDate("");
      setScheduledTime("");
    }
  };

  const loadPosts = async () => {
    setLoading(true);
    try {
      const data = await listPosts(filter || undefined);
      setPosts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (post: Post) => {
    const full = await getPost(post.id);
    setSelected(full);
    loadSchedule(full);
    setEditing(false);
  };

  const handleSave = async () => {
    if (!selected) return;
    await updatePost(selected.id, { body: editBody });
    const refreshed = await getPost(selected.id);
    setSelected(refreshed);
    setEditing(false);
    loadPosts();
  };

  const handleStatusChange = async (status: string) => {
    if (!selected) return;
    await updatePost(selected.id, { status });
    const refreshed = await getPost(selected.id);
    setSelected(refreshed);
    loadPosts();
  };

  const handleDelete = async () => {
    if (!selected || !confirm("Delete this post?")) return;
    await deletePost(selected.id);
    setSelected(null);
    loadPosts();
  };

  const handleScheduleSave = async () => {
    if (!selected) return;
    const scheduled_at = scheduledDate && scheduledTime
      ? new Date(`${scheduledDate}T${scheduledTime}:00`).toISOString()
      : null;
    await updatePost(selected.id, { scheduled_at } as Partial<Post>);
    const refreshed = await getPost(selected.id);
    setSelected(refreshed);
    loadPosts();
  };

  const inputStyle = {
    background: "var(--background)",
    border: "1px solid var(--border)",
    color: "var(--foreground)",
  };

  return (
    <div className="flex gap-6 max-w-[1400px]">
      {/* Post list */}
      <div className="w-72 flex-shrink-0 space-y-3">
        <h1 className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
          Posts
        </h1>

        {/* Filter */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full px-3 py-1.5 rounded-md text-sm"
          style={{ background: "var(--card)", border: "1px solid var(--border)", color: "var(--foreground)" }}
        >
          <option value="">All statuses</option>
          <option value="draft">Drafts</option>
          <option value="ready">Ready</option>
          <option value="posted">Posted</option>
        </select>

        {loading ? (
          <p style={{ color: "var(--muted)" }}>Loading...</p>
        ) : posts.length === 0 ? (
          <p className="text-sm" style={{ color: "var(--muted)" }}>
            No posts yet. Create one from the Create page.
          </p>
        ) : (
          <div className="space-y-2">
            {posts.map((post) => (
              <button
                key={post.id}
                onClick={() => handleSelect(post)}
                className="w-full text-left p-3 rounded-lg transition-opacity hover:opacity-90"
                style={{
                  background: selected?.id === post.id ? "var(--border)" : "var(--card)",
                  border: "1px solid var(--border)",
                }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <PillarBadge pillar={post.pillar} />
                  <span className="text-xs" style={{ color: "var(--muted)" }}>
                    {post.word_count}w
                  </span>
                </div>
                <p className="text-sm font-medium truncate">{post.topic}</p>
                <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
                  {post.status} &middot; {new Date(post.created_at).toLocaleDateString()}
                </p>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Post detail */}
      {selected ? (
        <div className="flex-1 min-w-0 flex gap-6">
          {/* Left column: Post content */}
          <div className="flex-1 min-w-0 space-y-4">
            <div>
              <h2 className="text-xl font-semibold">{selected.topic}</h2>
              <div className="flex items-center gap-2 mt-1">
                <PillarBadge pillar={selected.pillar} />
                <span className="text-sm" style={{ color: "var(--muted)" }}>
                  {selected.post_type} &middot; {selected.word_count} words
                </span>
              </div>
            </div>

            {/* Post body */}
            {editing ? (
              <div className="space-y-3">
                <textarea
                  value={editBody}
                  onChange={(e) => setEditBody(e.target.value)}
                  className="w-full h-64 p-3 rounded-lg text-sm"
                  style={{ background: "var(--background)", border: "1px solid var(--border)", color: "var(--foreground)" }}
                />
                <div className="flex items-center gap-3">
                  <span className="text-xs" style={{ color: "var(--muted)" }}>
                    {editBody.split(/\s+/).filter(Boolean).length} words
                  </span>
                  <button
                    onClick={handleSave}
                    className="px-3 py-1.5 rounded text-xs font-medium"
                    style={{ background: "var(--accent)", color: "var(--background)" }}
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditing(false)}
                    className="px-3 py-1.5 rounded text-xs font-medium"
                    style={{ background: "var(--border)", color: "var(--foreground)" }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <CopyBlock text={selected.body} />
            )}

            {/* Images */}
            {selected.images && selected.images.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold mb-2" style={{ color: "var(--muted)" }}>
                  Images
                </h3>
                <div className="flex gap-3 flex-wrap">
                  {selected.images.map((img) => (
                    <a
                      key={img.id}
                      href={img.public_url || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block rounded-lg overflow-hidden"
                      style={{ border: "1px solid var(--border)" }}
                    >
                      {img.public_url ? (
                        <img
                          src={img.public_url}
                          alt={img.image_type}
                          className="w-48 h-48 object-cover"
                        />
                      ) : (
                        <div
                          className="w-48 h-48 flex items-center justify-center text-xs"
                          style={{ background: "var(--card)", color: "var(--muted)" }}
                        >
                          {img.image_type}
                          {img.slide_number ? ` #${img.slide_number}` : ""}
                        </div>
                      )}
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Action buttons — equal width, horizontal */}
            <div className="grid grid-cols-3 gap-3">
              {selected.status === "draft" ? (
                <button
                  onClick={() => handleStatusChange("ready")}
                  className="py-2 rounded text-xs font-medium text-center"
                  style={{ background: "var(--pillar-wealth)", color: "var(--background)" }}
                >
                  Mark Ready
                </button>
              ) : (
                <button
                  onClick={() => handleStatusChange("draft")}
                  className="py-2 rounded text-xs font-medium text-center"
                  style={{ background: "var(--border)", color: "var(--foreground)" }}
                >
                  Back to Draft
                </button>
              )}
              <button
                onClick={() => { setEditing(true); setEditBody(selected.body); }}
                className="py-2 rounded text-xs font-medium text-center"
                style={{ background: "var(--accent)", color: "var(--background)" }}
              >
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="py-2 rounded text-xs font-medium text-center"
                style={{ background: "var(--pillar-risk)", color: "white" }}
              >
                Delete
              </button>
            </div>
          </div>

          {/* Right column: Schedule + Research Brief */}
          <div className="w-80 flex-shrink-0 space-y-5">
            {/* Schedule section */}
            <div
              className="p-4 rounded-lg space-y-3"
              style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
              <h3 className="text-sm font-semibold" style={{ color: "var(--accent)" }}>
                Schedule
              </h3>
              <div className="space-y-2">
                <div>
                  <label className="block text-xs mb-1" style={{ color: "var(--muted)" }}>Date</label>
                  <input
                    type="date"
                    value={scheduledDate}
                    onChange={(e) => setScheduledDate(e.target.value)}
                    className="w-full px-2 py-1.5 rounded text-sm"
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label className="block text-xs mb-1" style={{ color: "var(--muted)" }}>Time</label>
                  <input
                    type="time"
                    value={scheduledTime}
                    onChange={(e) => setScheduledTime(e.target.value)}
                    className="w-full px-2 py-1.5 rounded text-sm"
                    style={inputStyle}
                  />
                </div>
                <button
                  onClick={handleScheduleSave}
                  className="w-full py-1.5 rounded text-xs font-medium"
                  style={{ background: "var(--accent)", color: "var(--background)" }}
                >
                  {selected.scheduled_at ? "Update Schedule" : "Set Schedule"}
                </button>
                {selected.scheduled_at && (
                  <p className="text-xs" style={{ color: "var(--pillar-wealth)" }}>
                    Scheduled: {new Date(selected.scheduled_at).toLocaleString()}
                  </p>
                )}
              </div>
            </div>

            {/* Research Brief */}
            {selected.brief?.full_brief_md && (
              <div
                className="p-4 rounded-lg"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
              >
                <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--accent)" }}>
                  Research Brief
                </h3>
                <pre
                  className="text-xs whitespace-pre-wrap overflow-y-auto max-h-[500px]"
                  style={{ color: "var(--foreground)" }}
                >
                  {selected.brief.full_brief_md}
                </pre>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center h-64">
          <p className="text-sm" style={{ color: "var(--muted)" }}>
            Select a post to view details
          </p>
        </div>
      )}
    </div>
  );
}

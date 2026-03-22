"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listPosts, listIdeas, type Post, type Idea } from "@/lib/api";
import { PillarBadge } from "@/components/PillarBadge";

export default function Dashboard() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listPosts(), listIdeas()])
      .then(([p, i]) => {
        setPosts(p);
        setIdeas(i);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const drafts = posts.filter((p) => p.status === "draft");
  const ready = posts.filter((p) => p.status === "ready");
  const backlog = ideas.filter((i) => i.status === "backlog");

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: "var(--accent)" }}>
          Dashboard
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
          LinkedIn content pipeline overview
        </p>
      </div>

      {loading ? (
        <p style={{ color: "var(--muted)" }}>Loading...</p>
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Drafts", count: drafts.length, color: "var(--pillar-agentic)" },
              { label: "Ready", count: ready.length, color: "var(--pillar-wealth)" },
              { label: "Ideas Backlog", count: backlog.length, color: "var(--accent)" },
            ].map(({ label, count, color }) => (
              <div
                key={label}
                className="p-4 rounded-lg"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
              >
                <p className="text-3xl font-bold" style={{ color }}>
                  {count}
                </p>
                <p className="text-sm" style={{ color: "var(--muted)" }}>
                  {label}
                </p>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="flex gap-3">
            <Link
              href="/create"
              className="px-4 py-2 rounded-md text-sm font-medium"
              style={{ background: "var(--accent)", color: "var(--background)" }}
            >
              + Create Post
            </Link>
            <Link
              href="/ideas"
              className="px-4 py-2 rounded-md text-sm font-medium"
              style={{ background: "var(--border)", color: "var(--foreground)" }}
            >
              View Ideas
            </Link>
          </div>

          {/* Recent Posts */}
          {posts.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-3">Recent Posts</h2>
              <div className="space-y-2">
                {posts.slice(0, 5).map((post) => (
                  <Link
                    key={post.id}
                    href={`/posts?id=${post.id}`}
                    className="block p-4 rounded-lg hover:opacity-90 transition-opacity"
                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <PillarBadge pillar={post.pillar} />
                        <span className="text-sm font-medium">{post.topic}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs" style={{ color: "var(--muted)" }}>
                          {post.word_count}w
                        </span>
                        <span
                          className="text-xs px-2 py-0.5 rounded"
                          style={{
                            background:
                              post.status === "ready"
                                ? "var(--pillar-wealth)"
                                : "var(--border)",
                            color:
                              post.status === "ready"
                                ? "var(--background)"
                                : "var(--muted)",
                          }}
                        >
                          {post.status}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

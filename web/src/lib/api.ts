/**
 * lib/api.ts — FastAPI client for the LinkedIn content engine.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Pipeline
// ---------------------------------------------------------------------------

export interface PipelineRequest {
  topic: string;
  post_type?: string;
  image_type?: string;
  idea_id?: string;
}

export async function startFullPipeline(req: PipelineRequest) {
  return fetchAPI<{ run_id: string }>("/api/pipeline/full", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export async function startResearch(req: PipelineRequest) {
  return fetchAPI<{ run_id: string }>("/api/pipeline/research", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function getPipelineStreamURL(runId: string) {
  return `${API_URL}/api/pipeline/${runId}/stream`;
}

export async function getPipelineRun(runId: string) {
  return fetchAPI<Record<string, unknown>>(`/api/pipeline/${runId}`);
}

// ---------------------------------------------------------------------------
// Ideas
// ---------------------------------------------------------------------------

export interface Idea {
  id: string;
  number: number;
  title: string;
  post_type: string;
  pillar: string | null;
  theme: string | null;
  status: string;
  created_at: string;
}

export async function listIdeas(status?: string) {
  const q = status ? `?status=${status}` : "";
  return fetchAPI<Idea[]>(`/api/ideas${q}`);
}

export async function createIdeas(ideas: { title: string; post_type: string; pillar?: string; theme?: string }[]) {
  return fetchAPI<Idea[]>("/api/ideas", {
    method: "POST",
    body: JSON.stringify(ideas),
  });
}

export async function updateIdea(id: string, updates: Partial<Idea>) {
  return fetchAPI<Idea>(`/api/ideas/${id}`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}

// ---------------------------------------------------------------------------
// Posts
// ---------------------------------------------------------------------------

export interface Post {
  id: string;
  brief_id: string | null;
  idea_id: string | null;
  slug: string;
  topic: string;
  post_type: string;
  pillar: string;
  status: string;
  body: string;
  word_count: number;
  image_type: string | null;
  scheduled_at: string | null;
  posted_url: string | null;
  created_at: string;
  updated_at: string;
  images?: ImageRecord[];
  brief?: Brief | null;
}

export interface Brief {
  id: string;
  idea_id: string | null;
  topic: string;
  influencer_posts: unknown;
  web_research: string | null;
  synthesis: string | null;
  full_brief_md: string | null;
  researched_at: string;
}

export interface ImageRecord {
  id: string;
  post_id: string;
  image_type: string;
  storage_path: string;
  public_url: string | null;
  prompt: string | null;
  slide_number: number | null;
  created_at: string;
}

export async function listPosts(status?: string, pillar?: string) {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (pillar) params.set("pillar", pillar);
  const q = params.toString() ? `?${params}` : "";
  return fetchAPI<Post[]>(`/api/posts${q}`);
}

export async function getPost(id: string) {
  return fetchAPI<Post>(`/api/posts/${id}`);
}

export async function updatePost(id: string, updates: Partial<Post>) {
  return fetchAPI<Post>(`/api/posts/${id}`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}

export async function deletePost(id: string) {
  return fetchAPI<{ deleted: boolean }>(`/api/posts/${id}`, {
    method: "DELETE",
  });
}

// ---------------------------------------------------------------------------
// Influencers
// ---------------------------------------------------------------------------

export interface Influencer {
  name: string;
  url: string;
  pillar: string;
  note?: string;
}

export async function listInfluencers() {
  return fetchAPI<Influencer[]>("/api/influencers");
}

export async function addInfluencer(data: Influencer) {
  return fetchAPI<Influencer>("/api/influencers", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteInfluencer(name: string) {
  return fetchAPI<{ deleted: boolean }>(`/api/influencers/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
}

// ---------------------------------------------------------------------------
// Migration
// ---------------------------------------------------------------------------

export async function migrateIdeas() {
  return fetchAPI<{ migrated: number }>("/api/migrate/ideas", { method: "POST" });
}

export async function migrateDrafts() {
  return fetchAPI<{ migrated: number }>("/api/migrate/drafts", { method: "POST" });
}

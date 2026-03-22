-- LinkedIn Content Engine Schema
-- Run this in Supabase SQL Editor

CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    number INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    post_type TEXT NOT NULL CHECK (post_type IN ('thought-leadership', 'story', 'news', 'cta')),
    pillar TEXT CHECK (pillar IN ('agentic-ai', 'traditional-ml', 'wealth-asset-management', 'risk-management', 'general')),
    theme TEXT,
    status TEXT NOT NULL DEFAULT 'backlog' CHECK (status IN ('backlog', 'in-progress', 'drafted', 'published')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID REFERENCES ideas(id) ON DELETE SET NULL,
    topic TEXT NOT NULL,
    influencer_posts JSONB,
    web_research TEXT,
    synthesis TEXT,
    full_brief_md TEXT,
    researched_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brief_id UUID REFERENCES briefs(id) ON DELETE SET NULL,
    idea_id UUID REFERENCES ideas(id) ON DELETE SET NULL,
    slug TEXT UNIQUE NOT NULL,
    topic TEXT NOT NULL,
    post_type TEXT NOT NULL CHECK (post_type IN ('thought-leadership', 'story', 'news', 'cta')),
    pillar TEXT NOT NULL CHECK (pillar IN ('agentic-ai', 'traditional-ml', 'wealth-asset-management', 'risk-management', 'general')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'ready', 'scheduled', 'posted')),
    body TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    image_type TEXT CHECK (image_type IN ('diagram', 'branded', 'infographic', 'carousel', 'none')),
    scheduled_at TIMESTAMPTZ,
    posted_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    image_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    public_url TEXT,
    prompt TEXT,
    slide_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE SET NULL,
    idea_id UUID REFERENCES ideas(id) ON DELETE SET NULL,
    run_type TEXT NOT NULL CHECK (run_type IN ('full', 'research-only', 'write-only', 'image-only')),
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    current_phase TEXT,
    progress_pct INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_ideas_status ON ideas(status);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_pillar ON posts(pillar);
CREATE INDEX idx_images_post_id ON images(post_id);
CREATE INDEX idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX idx_briefs_idea_id ON briefs(idea_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ideas_updated_at BEFORE UPDATE ON ideas FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER posts_updated_at BEFORE UPDATE ON posts FOR EACH ROW EXECUTE FUNCTION update_updated_at();

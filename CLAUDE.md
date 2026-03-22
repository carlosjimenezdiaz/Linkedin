# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Who You Are Working With

**Carlos Jimenez Diaz** — AI/ML engineer and quantitative finance professional.

**Expertise pillars:**
- Agentic AI (multi-agent systems, LLM orchestration, autonomous workflows)
- Traditional ML (model deployment, feature engineering, real-world production ML)
- Wealth & Asset Management (quant strategies, portfolio optimization, ML in finance)
- Risk Management (model risk, regulatory frameworks, risk-adjusted returns)

**LinkedIn goal:** Establish Carlos as a credible SME across AI/ML and quantitative finance. Generate inbound consulting and side-work inquiries from CTOs, quant teams, and fintech founders.

---

## Running the Engine

```bash
# Activate the environment first
conda activate linkedin

# Full pipeline — picks next unprocessed idea from content/ideas.md
python -m engine.orchestrator --next-idea --image auto

# Full pipeline — explicit topic
python -m engine.orchestrator --topic "data leakage in financial ML" --type thought-leadership --image branded

# Research only (no writing, no image)
python -m engine.orchestrator --research-only --topic "LLM agents in finance"

# Skip research — use an existing brief
python -m engine.orchestrator --draft content/drafts/{slug}/brief.md --image diagram

# Image types: diagram | branded | infographic | carousel | auto | none
```

**Required env vars in `.env`:** `APIFY_TOKEN`, `OPENROUTER_API_KEY`, `FAL_KEY`, `IDEOGRAM_API_KEY`

**Playwright must be installed** in the active conda env for diagram/carousel rendering:
```bash
pip install playwright && playwright install chromium
```

---

## Architecture

The engine runs as a 3-phase CLI pipeline orchestrated by `engine/orchestrator.py`:

### Phase 1 — Research (`engine/research.py`)
1. **Apify** scrapes recent posts from `profile/influencers.json` using actor `harvestapi~linkedin-profile-posts`. Posts are scored by engagement (likes + 3×comments + 5×shares), filtered to last 30 days, top 5 kept.
2. **Perplexity** (`perplexity/sonar` via OpenRouter) runs a web research query on the topic.
3. **Claude haiku** (`anthropic/claude-3.5-haiku` via OpenRouter) synthesizes both into a `brief.md` written to the draft folder.

### Phase 2 — Write (`engine/generate.py`)
- Calls `anthropic/claude-sonnet-4-5` via OpenRouter.
- System prompt loads: `profile/style.md`, `profile/audience.md`, last 3 published posts from `content/published/`.
- Output is a 150–300 word post saved as `post.md` with YAML frontmatter (type, pillar, status, word_count, image_type, etc.).
- Pillar and image type are auto-inferred from post text.

### Phase 3 — Image (`engine/images.py`, `engine/diagram.py`, `engine/carousel.py`)

| Image type | Generator | Output | Best for |
|---|---|---|---|
| `diagram` | Claude haiku → HTML template → Playwright | `diagram.png` 1200×628 | Most posts (default) |
| `branded` | fal.ai/Flux (`fal-ai/flux/dev`) | `main.png` 16:9 | Story/CTA posts |
| `infographic` | Ideogram v3 API | `infographic.png` 1:1 | Stats-heavy posts |
| `carousel` | Claude haiku → HTML template → Playwright | `carousel/slide-NN.png` 1080×1080 | 3+ numbered insights |

**Diagram generation** (`engine/diagram.py`) is template-based — Claude returns JSON (template name + text slots only), Python fills pre-built HTML/CSS templates, Playwright renders PNG. No free-form SVG. Templates live in `engine/templates/diagram_*.html` (4 types: `3-column`, `flow`, `comparison`, `breakdown`).

### Models used (all via OpenRouter)
| Role | Model |
|---|---|
| Post writer | `anthropic/claude-sonnet-4-5` |
| Fast synthesis / diagram content | `anthropic/claude-3.5-haiku` |
| Web research | `perplexity/sonar` |

### Key paths
| Path | Purpose |
|---|---|
| `engine/config.py` | All env vars, model names, brand constants, path constants |
| `engine/packager.py` | `get_next_idea()` parses `content/ideas.md`; `make_slug()` builds date-prefixed folder names |
| `profile/influencers.json` | List of LinkedIn profile URLs to scrape via Apify |
| `content/ideas.md` | Running backlog — `[#NNN]` index, one idea per line |
| `content/drafts/{slug}/` | One folder per generated post: `brief.md`, `post.md`, `images/` |
| `content/published/` | Archive of posted content — the 3 most recent drive voice grounding |
| `inspiration/` | Visual reference bank (manual curation): `single-image/`, `infographics/`, `carousels/` |

---

## Content Workflow

```
Ideate  → /linkedin ideas [theme]          → appends to content/ideas.md
Draft   → /linkedin draft [number]         → creates file in content/drafts/
Create  → /linkedin create [type] [topic]  → full post, ready to copy
Full    → /linkedin full [topic]           → suggests orchestrator command
Visual  → /linkedin visual [draft-folder]  → recommends image type + command
Publish → /linkedin publish [draft-file]   → final polish + copy-paste block
Style   → /linkedin style                  → analyzes published posts, proposes updates
Calendar→ /linkedin calendar [weeks]        → 2-week posting calendar
```

**ALWAYS read before generating content:**
1. `profile/style.md` — voice, tone, formatting rules
2. `profile/topics.md` — content pillars and seed ideas
3. `profile/audience.md` — who Carlos is writing for
4. Last 3 files in `content/published/` — these override style.md when they exist

---

## Content Boundaries

- Post length: **150–300 words** (never under 100, never over 350)
- No corporate buzzwords: no "game-changing", "revolutionary", "disruptive", "in today's fast-paced world"
- No "I'm excited/humbled/proud to share"
- Never fabricate statistics — use real data from research or note it is approximate
- CTAs must feel natural — never "like and share"
- 3–5 hashtags at the very end, on their own line
- Always output posts in a clearly delimited block for copy-paste

---

## Brand Constants (defined in `engine/config.py`)

| Constant | Value |
|---|---|
| `BRAND_BG_COLOR` | `#0a1628` (dark navy) |
| `BRAND_ACCENT_COLOR` | `#c9a84c` (gold) |
| Pillar accent — agentic-ai | `#4a9eff` |
| Pillar accent — traditional-ml | `#c9a84c` |
| Pillar accent — wealth-asset-management | `#50c878` |
| Pillar accent — risk-management | `#e05c5c` |

---

## Future: LinkedIn API

When ready to automate publishing, add `api/` directory. All draft files already use YAML frontmatter with `scheduled` and `posted_url` fields for this transition.

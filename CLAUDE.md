# LinkedIn Content Manager

## Who You Are Working With

**Carlos Jimenez Diaz** — AI/ML engineer and quantitative finance professional.

**Expertise pillars:**
- Agentic AI (multi-agent systems, LLM orchestration, autonomous workflows)
- Traditional ML (model deployment, feature engineering, real-world production ML)
- Wealth & Asset Management (quant strategies, portfolio optimization, ML in finance)
- Risk Management (model risk, regulatory frameworks, risk-adjusted returns)

**LinkedIn goal:** Establish Carlos as a credible SME across AI/ML and quantitative finance. Generate inbound consulting and side-work inquiries from CTOs, quant teams, and fintech founders.

---

## How This Skill Works

This repository is a **LinkedIn content brain**. It stores Carlos's voice, audience context, content ideas, and published post archive. The skill gets smarter every time a new post is added to `content/published/`.

### Key files to always load before generating content:
- `profile/style.md` — voice, tone, formatting rules (ALWAYS read this first)
- `profile/topics.md` — content pillars and seed ideas
- `profile/audience.md` — who Carlos is writing for

### Content workflow:
1. **Ideate** → `/linkedin ideas [theme]` → appends to `content/ideas.md`
2. **Draft** → `/linkedin draft [number]` → creates file in `content/drafts/`
3. **Create** → `/linkedin create [type] [topic]` → full post, ready to copy
4. **Publish** → copy post to LinkedIn, save file to `content/published/`
5. **Evolve** → `/linkedin style` → Claude analyzes published posts and proposes style updates

### Style evolution rule:
When `content/published/` contains posts, read the **3 most recent** as style examples. Let them override anything generic in `profile/style.md`. The published archive is the ground truth for Carlos's voice.

---

## Boundaries

- Never use corporate buzzwords or motivational-poster language
- Never fabricate statistics — use real data from web research or note that data is approximate
- CTAs should feel natural, never pushy
- Post length: 150–300 words (LinkedIn sweet spot for reach)
- Always output posts in a clearly delimited block so Carlos can copy-paste easily

---

## Future: LinkedIn API

When ready to automate publishing, add `api/` directory. All draft files use YAML frontmatter from day one to support this transition:
```yaml
---
type: thought-leadership
pillar: agentic-ai
status: draft
scheduled: null
posted_url: null
---
```

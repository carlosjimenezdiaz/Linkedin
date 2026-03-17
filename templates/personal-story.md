# Template: Personal Story Post

**Use when:** Sharing a specific experience, mistake, or turning point. Stories build trust and humanize expertise. Best used 1x per week max.

**Target length:** 200–300 words

**Goal:** Leave the reader with a lesson they can apply, delivered through Carlos's direct experience.

---

## Structure

```
[HOOK — 1 sentence that sets up the story with tension or specificity]
  ("I almost shipped a model that would have cost us 7 figures." not "I learned something important...")

[THE SITUATION — 2–3 sentences: context, what was happening]

[THE TURNING POINT — 1–2 sentences: what changed, what went wrong or right]

[WHAT I LEARNED — 2–4 sentences: the actual insight. Be specific.]

[BROADER IMPLICATION — 1–2 sentences: why does this matter beyond your situation?]

[CTA — low-friction, invites shared experience or consultation]

[HASHTAGS — 3–5]
```

---

## Hook Examples

- "I spent 3 months building a model that should never have been built."
- "[Year]. My first production agentic system. It went live. Then it immediately broke."
- "The most useful thing a senior quant ever told me: 'Your model is probably right. Your data is definitely wrong.'"
- "I made a $[vague]k mistake in my first financial ML deployment. Here's the full breakdown."
- "Nobody warned me about [specific thing] when I moved from research to production."

---

## Story Quality Rules

- **Be specific** — name the type of system, the kind of problem, the approximate scale. Vague stories feel fake.
- **Own the failure** — if it's a mistake story, don't soften it. Own it. That's what makes it credible.
- **One lesson** — don't try to teach five things. One clear, actionable takeaway.
- **No humble-bragging** — "I thought I knew everything but then I learned" is more effective than "I built something amazing and here's what I learned."

---

## CTA Options

- "Has anyone else run into this? Genuinely curious how others handled it."
- "If you're building something similar and want to sanity-check your approach, let's talk."
- "What's the most expensive lesson your team learned in production? Drop it in the comments."

---

## Example Post (illustrative)

```
I once deployed a risk model that passed every internal review. Clean code, solid methodology, good backtests.

It was wrong in a way nobody caught for 6 months.

The problem: we had a lookback bias in one of the input features. Small, subtle. It inflated the model's confidence in calm regimes — exactly when you need the model to be cautious.

We only found it because a junior analyst noticed the model's outputs were suspiciously correlated with a feature we'd excluded from the final version. Turned out it was a data pipeline artifact, not the model.

The lesson wasn't technical. It was organizational: we had a review process for the model, but no review process for the data lineage.

The math gets reviewed. The assumptions in the infrastructure don't.

If you're running model validation at a firm and want to stress-test your data pipeline assumptions, happy to do a working session.

#RiskManagement #ModelRisk #MLOps #QuantFinance #FinancialML
```

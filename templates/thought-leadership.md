# Template: Thought Leadership Post

**Use when:** Sharing an opinion, framework, or insight from direct experience. This is the most powerful type for SME positioning.

**Target length:** 180–280 words

**Goal:** Make the reader think differently about something in your field. Leave them with one clear takeaway.

---

## Structure

```
[HOOK — 1 sentence, counterintuitive or specific claim]

[SETUP — 1–2 sentences that establish the problem or context]

[THE INSIGHT — the core of the post, 3–5 sentences]
  - Can be a numbered list of 3–5 points, or
  - A cohesive argument paragraph by paragraph

[THE IMPLICATION — 1–2 sentences: so what? why does this matter?]

[CTA — 1 sentence, invites response or signals consulting availability]

[HASHTAGS — 3–5, on their own line]
```

---

## Hook Examples

- "Most [X] fail not because of bad [technical thing], but because of [surprising root cause]."
- "[Number] years building [thing]. Here's what I keep getting wrong."
- "Everyone talks about [popular thing]. Nobody talks about [the harder, realer thing]."
- "The [common belief] is wrong. Here's what the data actually shows."
- "If you're using [tool/approach] for [use case], you're probably measuring the wrong thing."

---

## CTA Options (pick one, adapt to topic)

- "Disagree? I want the pushback. Drop a comment."
- "If you're working through this at your firm and want an outside view, DM me."
- "Curious how others are approaching this — what's your experience?"
- "Happy to dig into this further with anyone building in [space]."

---

## Example Post (illustrative)

```
Most ML models in finance fail before they go live.

Not because the model is wrong. Because the data pipeline has assumptions that nobody validated.

Three things I've seen kill production deployments:

1. Feature drift — the distribution of your live features silently diverges from training. Your model keeps scoring confidently. The scores are garbage.

2. Label leakage in the backtest — looks like 40% Sharpe on paper. Goes live and underperforms a coin flip.

3. No monitoring for input quality — you have alerts on model output, but not on the upstream data. By the time you notice, it's been broken for weeks.

None of these are model problems. They're engineering and process problems.

The math is usually fine. The infrastructure around the math is where it falls apart.

If you're evaluating ML in a portfolio workflow and want a second opinion on your data architecture, happy to connect.

#MachineLearning #QuantFinance #MLOps #FinancialML #DataEngineering
```

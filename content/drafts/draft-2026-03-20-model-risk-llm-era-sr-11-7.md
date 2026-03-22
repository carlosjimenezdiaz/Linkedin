---
idea: "#010"
type: thought-leadership
pillar: risk-management
status: draft
word_count: 262
image_type: diagram
created: 2026-03-20
scheduled: ""
posted_url: ""
---

SR 11-7 assumes your model gives the same output every time. LLMs don't.

The Fed's model risk guidance has been the gold standard since 2011 — built for credit scoring models, VaR engines, and pricing libraries. It works because those models are static and deterministic. Feed them the same inputs tomorrow, you get the same outputs.

LLMs break three foundational assumptions in that framework:

**Non-determinism.** SR 11-7 validation is built on reproducibility. Same input → verifiable output. A system that produces different responses to identical prompts can't be validated the same way.

**Validation cadence.** The framework assumes periodic review cycles. LLMs drift in ways that make annual validation meaningless — model weights change, prompt behavior shifts, and the system you validated six months ago isn't the one running today.

**Model definition.** SR 11-7 defines a model as a quantitative method applying statistical, economic, or mathematical theory. An LLM summarizing earnings calls and flagging risk factors doesn't fit that taxonomy cleanly. Most MRM teams are shoehorning it in — and it shows.

In February 2026, the Treasury released AI-specific guidance for financial services, including a NIST AI RMF adaptation. It doesn't replace SR 11-7. It signals that regulators know the gap exists.

Risk teams aren't ignoring this. They're improvising. And improvised governance in a regulated environment is an audit waiting to happen.

If you're trying to map LLM deployments to your MRM framework and want a practitioner's perspective, DM me.

#ModelRisk #RiskManagement #LLMEngineering #FinancialRisk #Regulation

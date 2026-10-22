---
name: architecture-adr
description: Discuss three requirement-driven software architectures, compare concrete trade-offs, support an explicit user decision, and draft and revise an architecture decision record (ADR). Use for architecture exploration, selection, or ADR drafting and review with ongoing discussion notes.
---

# Architecture discussion and ADR workflow

Guide an interactive decision, not a predetermined answer. Keep explanations concise and understandable, but make implementation and maintenance costs concrete. Use only the phases the user authorizes; do not implement the system.

## 1. Establish evidence, scope, and notes

- Read the supplied requirements, task instructions, existing discussion, and any current ADR. Follow the latest corrections without erasing the history of earlier proposals.
- Confirm the requested output paths and current phase. Ask only for missing information that blocks progress; otherwise preserve it as unknown.
- Start or continue a discussion record before presenting proposals. If no notes path is supplied, agree on one. Record requirement sources, proposals, questions, user corrections, revisions, decisions, unresolved items, and the next stopping point. Summaries are sufficient; do not fabricate dialogue or acceptance.
- Separate **stated requirements**, **unknowns**, and **conditional scenarios**. Do not infer team size, project lifetime, platform familiarity, traffic, budget, or deployment from an assignment or application domain.
- Distinguish required behavior from possible additions: for example, storing an event is not the same as delivering a notification. Identify ambiguous search, time, data-source, and security semantics when relevant.

## 2. Discuss three viable architectures

Choose three materially different designs that could satisfy the requirements. Do not always choose the same patterns or bias the set toward a favorite. Explain overlaps: code organization, deployment model, data model, and vendor services are different dimensions, not necessarily mutually exclusive alternatives.

For each proposal, cover:

1. **Components and responsibilities:** where the required behavior and data live.
2. **Communication:** browser/backend boundaries, internal calls or APIs, data ownership, and any asynchronous work. Trace a representative user action.
3. **Advantages:** connect each benefit to a requirement or an explicitly conditional scenario.
4. **Disadvantages:** identify the cost paid for those benefits.
5. **Concrete difficulties:** describe at least one implementation problem and one ongoing maintenance problem, including failure behavior and a practical mitigation.

Consider only applicable issues: authentication and authorization, consistency, transactions, retries and duplicate effects, deletion, external-provider failures, indexing, timezones, backups, observability, deployment, and resource limits. Explain technical terms briefly rather than presenting a generic checklist as the design.

Use security examples accurately: derive identity from a trusted authenticated context; enforce ownership on private data, not on public resources merely referenced by a user's records.

Finish with a comparison table using the same criteria for all three, then a provisional recommendation, its biggest trade-off, and conditions that would change it. Avoid unsupported cost or performance rankings. **Record the discussion and wait for feedback. Do not automatically create an ADR.**

## 3. Challenge the recommendation and support a decision

- Answer objections directly. Distinguish less infrastructure administration from less total implementation and maintenance work.
- Attribute limitations to their actual cause: a particular database or provider limitation is not automatically a property of an entire architectural style.
- When recommending a technology, say whether requirements favor it or it is merely a familiar default. Compare relevant alternatives without inventing deployment constraints; defer choices that have no supporting evidence.
- Explain both initial implementation and ongoing work using concrete flows, such as a partial deletion or retry after a provider timeout. Identify trade-offs shared by multiple options.
- Revise the recommendation when evidence changes. Ask focused questions only where answers could affect the decision.
- Treat a user's preference as a preference, not acceptance. Record exactly what is accepted and what remains open. Architecture acceptance does not automatically select a database, framework, provider, or hosting platform.

## 4. Draft the ADR when requested

An ADR may be drafted before acceptance; use its status to make that clear. Reuse the discussion instead of reopening settled comparisons or introducing technologies without a reason.

Use this compact structure:

```markdown
# ADR-<number>: <decision title>

**Status:** Draft / Accepted (choose the actual state)
**Scope:** <what this record decides>

## Context
<relevant requirements and source links>

## Decision
<architecture, main reasons, and biggest trade-off in one short paragraph>

### Components and communication
<responsibility table, simple text/Mermaid diagram, and key flows>

## Alternatives considered
<brief comparison of the three discussed options and their disposition>

## Consequences and implementation difficulties
<benefits, concrete costs/failure modes, and mitigations>

## Unresolved choices
<unknown constraints, deferred selections, and evidence needed>

## Validation and reconsideration
<observable checks and conditions that warrant revisiting the decision>
```

Keep status at the top and consolidate unresolved choices in their section. Elsewhere describe consequences without repeatedly declaring the same unknowns. Keep titles, comparison wording, and Decision wording consistent with the current status. Diagrams must agree with the described boundaries and flows.

Do not turn hypothetical validation into claims of completed tests. Do not invent workload thresholds. Link to project sources, not to this skill's directory.

## 5. Review, finalize, and stop

- Invite user review of correctness, missing/excess content, clarity, structure, and the diagram. Wait for their response.
- Apply requested revisions narrowly. Preserve useful implementation detail; do not expand the comparison or add technology choices unless requested or necessary to correct an error.
- Update the discussion record after each meaningful exchange, preserving corrections and the scope of acceptance.
- Mark the ADR **Accepted** only on explicit user acceptance. Update stale proposal language and record deferred choices separately. Do not force extra review rounds or manufacture feedback.
- Check that the ADR and notes agree on status, decision scope, flows, and unresolved choices.
- Report changed paths briefly and stop at the requested boundary. Do not implement the application, run a fresh-session exercise, generate a comparison report, or proceed to another task without authorization.

No scripts, extra tooling, predetermined architecture, database, or vendor are required by this workflow.

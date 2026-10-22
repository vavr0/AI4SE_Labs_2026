# RecipeCove: before/after comparison

## Evidence and scope

[Task 3](Tasks/Task_3.md#task-3-assignment) asks whether repeating architecture exploration and ADR creation with a skill achieves the goal faster. This comparison uses both discussion records, both saved ADRs, and [the skill](skills/architecture-adr/SKILL.md). The records summarize exchanges rather than providing timed execution traces; statements below distinguish recorded behavior from inferred effects.

## Initial response quality and unsupported assumptions

**Before:** The first response already supplied three architectures, components, communication, concrete difficulties, a comparison, and a provisional recommendation. It also identified optional LLM use and uncertain reminder delivery. However, it introduced PostgreSQL without a requirement-specific justification and used a small-team/modest-usage scenario. The record explicitly labels that scenario unconfirmed, so it should not be treated as an established project constraint. Its initial comparison also used broad speed/cost rankings, such as “Fast with provider fit” and “Usually highest baseline” ([initial proposals and comparison](discussion_before.md#discussion-record-initial-proposals)).

**After:** The first response left database, framework, vendor, and hosting choices open; separated deployment from code organization; and gave implementation **and maintenance** failure examples for each option. It correctly distinguished authenticated ownership of favorites from ownership of public recipes from the outset. The comparison emphasized mechanisms rather than unsupported cost rankings ([proposals](discussion_after.md#assistant-proposals), [comparison](discussion_after.md#shared-concerns-and-comparison)). This aligns with the skill's [proposal rules](skills/architecture-adr/SKILL.md#2-discuss-three-viable-architectures), but alignment alone does not prove causation.

The after response still provisionally assumed logout preserves saved data, explicitly pending confirmation; this was not initially a confirmed requirement ([requirements and unknowns](discussion_after.md#requirements-and-unknowns)). It was subsequently agreed by the user, not silently promoted to fact.

## Corrective feedback

**Before:** Two architecture follow-ups challenged serverless maintenance and PostgreSQL selection. The assistant then clarified overlapping architecture dimensions and withdrew the database preference. ADR review requested less repetition, followed by a favorite-flow clarification at acceptance ([serverless follow-up](discussion_before.md#follow-up-why-not-prefer-serverless-for-less-administration), [database follow-up](discussion_before.md#follow-up-why-postgresql-rather-than-sqlite-or-mysql), [revision](discussion_before.md#task-2--adr-revision-1-reduce-repetition), [acceptance](discussion_before.md#task-2--final-revision-and-acceptance)).

**After:** No equivalent serverless/database challenge is recorded before drafting. Feedback instead preserved reminder uncertainty, removed conversation history from Context, and resolved logout semantics. Explicit final acceptance remained necessary ([Task 2 authorization](discussion_after.md#user-feedback-and-task-2-authorization), [revisions](discussion_after.md#user-requested-draft-revisions), [acceptance](discussion_after.md#final-acceptance)). Thus, fewer foundational correction exchanges are visible, not an absence of review.

## Final ADR quality and artifact gaps

Both ADRs are marked **Accepted**, document the modular-monolith decision, show communication, compare alternatives, retain unresolved technologies, and propose future validation rather than claiming completed tests.

The [before ADR](ADR_001_RecipeCove.md#decision) explicitly selects relational persistence. Its finalization is incomplete: the title still says “Proposed,” the alternatives table says “Proposed starting structure” and “Not selected in this draft,” and reconsideration refers to “the proposal” despite Accepted status. These are artifact inconsistencies, not evidence that acceptance never occurred.

The [after ADR](ADR_001_RecipeCove_after.md#decision) consistently describes the selected architecture and specifies one transactional database without selecting a product. Its flows additionally cover event retries, logout preservation, and removal of stale private references; its consequences distinguish provider timeout from a nonexistent recipe ([components and communication](ADR_001_RecipeCove_after.md#components-and-communication), [consequences](ADR_001_RecipeCove_after.md#consequences-and-implementation-difficulties)). These are concrete documentation gains, not demonstrated runtime improvements. Neither artifact proves implementation correctness or completed validation; unresolved reminder behavior remains a requirement gap, explicitly disclosed rather than fixed here.

## Is faster completion supported?

**Not established.** The after record shows fewer foundational challenges, which suggests reduced conversational rework. Neither record supplies elapsed time, drafting duration, or comparable effort measurements; exchange counts cannot establish speed.

Task familiarity is a confounder: the skill encodes lessons from the earlier RecipeCove exercise, and the repeated task uses the same domain. The after record reports a fresh session without reading baseline artifacts, but that does not remove knowledge embedded in the skill. Model identity/settings and other execution conditions are unknown. The evidence supports better upfront handling of several previously corrected issues and cleaner finalization—not a measured speed gain or an isolated causal effect of the skill.

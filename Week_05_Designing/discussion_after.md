# RecipeCove — architecture discussion after applying the skill

## Scope and sources
- User requested a fresh Task 1 discussion using `skills/architecture-adr/SKILL.md`, without reading previous discussion or ADR, copying their decisions, or modifying baseline files.
- Sources read: `Tasks/Task_1.md`, `Tasks/data/RecipeCove.txt`, and the specified skill.
- Authorized phase: discuss three architectures, recommend one provisionally, and wait for feedback. No ADR, Task 2, or application implementation authorized.
- These are summaries of the current exchange, not a fabricated transcript. No user acceptance has occurred.

## Requirements and unknowns
Stated requirements: public recipe-name search, recipe and ingredient details, diet-based recipe discovery through a chatbot, Google-account registration/login, logout, profile, private favorites, and personal calendar creation/deletion with recipe events.

Unknown: recipe/ingredient data source and licensing; search matching/ranking; diet definitions and reliability; chatbot behavior and whether it needs an LLM; whether a reminder means a visible calendar entry or active notification; date-only versus timed events/timezones; scale, team experience, budget, hosting, and availability goals. Story 7's logout wording is unclear; assume ending the session without deleting saved data, pending confirmation.

## Assistant proposals
The alternatives differ principally in deployment and data ownership. All can have modular code, use managed infrastructure, or support a chatbot without an LLM. No database, framework, vendor, or hosting platform is selected.

### A. Modular monolith
- Components: browser UI; one backend deployable with identity/profile, recipe/ingredient catalog and search, diet/chat, favorites, and calendar modules; one database with logical module ownership. Google identity and an optional external recipe provider are outside the backend.
- Communication: browser calls backend API over HTTPS; modules call each other in process. A favorite request derives user identity from the authenticated session, validates the public recipe reference, and inserts a unique user/recipe link. Recipe details remain publicly accessible; private favorites/calendars require ownership checks.
- Benefits: direct calls and shared database transactions simplify required favorites/calendar operations and debugging. Diet/chat can reuse catalog filtering without a network hop.
- Disadvantages: a single deployment couples module releases and scaling; slow chat/provider calls can consume capacity needed by normal requests.
- Implementation difficulty: define module boundaries and enforce private-record ownership on every operation. Delete calendar and events transactionally; use database uniqueness for duplicate favorites and idempotency keys for retried event creation.
- Maintenance difficulty/failure: module coupling can grow; slow external dependencies affect the shared backend. Mitigate with boundary tests, bounded request timeouts/concurrency, and explicit unavailable responses. Use database backups and test restoration. Add background jobs only if confirmed behavior requires them.

### B. Serverless/backend-as-a-service composition
- Components: browser UI; managed Google-compatible identity; managed database and access policies for profiles/favorites/calendars; serverless functions for catalog/search and diet/chat, privileged writes, and external-provider secrets. Hosting provider remains undecided.
- Communication: browser may read/write permitted private data directly through authenticated managed APIs; functions handle trusted operations and provider calls. Adding a calendar event submits an authenticated request, validates calendar ownership and recipe reference, then atomically writes the event through supported database operations. Identity comes from verified authentication, not a submitted user ID.
- Benefits: managed identity/runtime removes some infrastructure administration; functions can isolate slow chat work from other endpoints. Managed scale-to-zero is useful only if traffic and provider pricing make it so.
- Disadvantages: browser policies plus function authorization create multiple security surfaces; provider APIs/limits shape implementation and portability. Less server administration is not necessarily less total work.
- Implementation difficulty: test access policies against cross-user access and implement atomic calendar deletion. Prefer a database with suitable transactions/cascades; if a chosen store cannot delete all events atomically, hide a deleting calendar and retry durable cleanup until complete. This is a storage-provider limitation, not inherent to serverless.
- Maintenance difficulty/failure: function timeouts, database quotas, and configuration drift complicate diagnosis. Propagate request IDs, monitor limits, version policies, and use idempotent writes so retrying after a timeout cannot create duplicate events. Provider backup/export and restore procedures still need verification.

### C. Domain-oriented services
- Components: browser plus API gateway; identity/profile service, catalog/search/ingredient service, diet/chat service, and personal-data service owning favorites/calendars/events. Each service owns its data; personal-data groups calendar/events to retain local transactions.
- Communication: browser uses gateway; services use authenticated APIs. Chat asks catalog for candidates matching a structured diet filter and returns recipe references. Adding an event checks identity, calendar ownership, and recipe reference, then commits locally. Private owners are not inferred from caller-supplied IDs.
- Benefits: diet/chat can be deployed and scaled separately; independent teams or substantially different workloads could justify service ownership. Catalog failures can be isolated from reading existing personal data.
- Disadvantages: extra deployments, network latency, distributed tracing, API compatibility, and no simple transaction spanning service databases. No stated requirement currently establishes a need for these costs.
- Implementation difficulty: handle catalog timeout during event creation without confusing failure with a nonexistent recipe. Return a retryable error without writing; use an idempotency key to handle a committed request whose response was lost. Define behavior for stale recipe references; a missing public recipe must not prevent deleting a private favorite/calendar event.
- Maintenance difficulty/failure: a catalog outage can cascade into chat and new writes; use bounded timeouts and circuit breakers (temporarily stop calls to a failing dependency), and keep private reads independent where possible. Trace requests across services, coordinate compatible API changes, and back up/restore each data owner. An event broker is not required merely because services are separate.

## Shared concerns and comparison
All designs must validate Google authentication, protect private records, preserve public recipe access, handle unavailable recipe/chat providers, and retain recoverable data. Recipe source ingestion versus live lookup remains undecided. If an LLM is used, recommend only validated catalog recipes and enforce dietary filters outside generated prose; ingredient data uncertainty must not become a medical-safety guarantee. Visible calendar events do not automatically imply email/push notifications; notification delivery would add scheduling, retries, and duplicate-delivery handling.

| Criterion | A: Modular monolith | B: Serverless/BaaS | C: Domain services |
|---|---|---|---|
| Deployment/operations | One backend plus database | Managed services/functions, policies and quotas | Multiple services, data stores and APIs |
| Calendar consistency | One database transaction | Depends on chosen store's transactions | Local personal-data transaction; recipe references cross boundaries |
| Security focus | Central session and ownership checks | Database policies plus function checks | Gateway identity plus service-level authorization |
| Chat/provider failures | Shared runtime; bound concurrency | Separate functions; limits/timeouts matter | Separate service; prevent cascading failures |
| Change/scaling independence | Modules release/scale together | Functions independently within provider model | Services independently, with API coordination |
| Main implementation/maintenance cost | Preserve module boundaries and shared-runtime health | Policies, integration, quotas and provider-specific recovery | Network failures, tracing, API compatibility and distributed data |

## Provisional recommendation and stopping point
Assistant recommends A, the modular monolith: required personal-data transactions and catalog/chat integration can remain within one backend without introducing distributed coordination. Biggest trade-off: coupled deployment and scaling, especially when chat calls are slow. This is not a claim that it is universally cheaper or faster.

B becomes more attractive with evidence of team expertise in a suitable managed platform and compatible query/transaction/runtime needs. C becomes more attractive with independent teams, genuinely separate scaling needs, or strong isolation requirements. Those conditions are unknown, not assumed.

Questions offered for feedback: Does the user prefer a different trade-off? Does a calendar reminder require active delivery or just a calendar entry? Is there a mandated recipe source or chatbot technology?

Status at the end of Task 1's initial exchange: proposals presented; recommendation provisional; awaiting user feedback. No architecture accepted and no technology selected. Only this discussion record had been created.

## User feedback and Task 2 authorization
- User: “I agree with the modular-monolith recommendation as the proposed architecture.” This supports the proposal; it is not final acceptance of an ADR.
- User clarified that reminder delivery is unspecified and must remain unresolved. Neither email/push delivery nor calendar-only satisfaction is assumed.
- User authorized reading `Tasks/Task_2.md` and creating `ADR_001_RecipeCove_after.md` from this new discussion, while continuing these notes.
- User required that unsupported technology choices stay open; baseline discussion/ADR remain unread and unchanged. No implementation or comparison report is authorized. Next stopping point: user review of the draft.

## ADR draft produced
- Read `Tasks/Task_2.md` and created `ADR_001_RecipeCove_after.md` with **Draft** status.
- Draft covers requirements and context, proposed modular-monolith decision, component responsibility table, Mermaid communication diagram, key flows, the three alternatives, implementation/maintenance difficulties and mitigations, consolidated unresolved choices, and future validation/reconsideration criteria.
- Google identity follows the requirements; database product, frameworks, hosting, other providers, and LLM use remain open. Reminder delivery and time semantics remain unresolved.
- Draft distinguishes public recipe access from private favorites/calendar ownership, local calendar-deletion transactions, retry safety, conditional external dependencies, and shared-runtime failure risks.
- No tests or implementation are claimed. Baseline files were not read or modified; no comparison report was written.
- Status after draft creation: modular monolith agreed as the proposed architecture; ADR draft awaited user review and was not marked Accepted.

## User-requested draft revisions
- User requested that Context focus on application requirements and the architectural problem, removing Task 1/Task 2 conversation history while retaining source links.
- User explicitly agreed that logout ends the current application session while preserving the user's profile, favorites, and calendars, and requested removing logout from unresolved choices.
- User required architecture and diagram to remain unchanged; reminder delivery and unsupported technology choices remain open.
- Assistant revised `ADR_001_RecipeCove_after.md` narrowly: replaced the Context history paragraph with the architectural problem and agreed logout behavior, retained all source links, updated the login/logout flow, and removed the unresolved logout item.
- Architecture and diagram are unchanged. Earlier notes above retain the history of logout being uncertain; this exchange resolves it.
- Status after revisions: ADR remained **Draft**, awaiting the user's final review. No implementation, comparison report, or baseline-file changes.

## Final acceptance
- User explicitly stated: “I accept ADR_001_RecipeCove_after.md. Finalize its wording and record my acceptance in discussion_after.md.”
- Assistant marked `ADR_001_RecipeCove_after.md` **Accepted**, removed stale proposal wording from its title and decision, and aligned the alternatives table and related wording with the selected architecture.
- Acceptance covers the modular-monolith architecture, responsibilities, communication, and data ownership described in the ADR, including the agreed logout behavior. Architecture and diagram remain unchanged.
- Reminder delivery, unsupported technology selections, and all other listed unresolved choices remain open. Future validation checks are not claims of completed tests.
- Final status: ADR accepted and finalized; acceptance recorded here. No application implementation, comparison report, or baseline-file changes. Work stops at this boundary.

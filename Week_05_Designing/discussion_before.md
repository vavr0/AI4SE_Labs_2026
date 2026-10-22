# RecipeCove — architecture discussion before implementation

## Discussion record: initial proposals

**User request:** Read `Tasks/Task_1.md` and `Tasks/data/RecipeCove.txt`; propose three architectures with components, communication, benefits, drawbacks, and concrete implementation difficulties. Finish with a comparison and recommendation, then wait for feedback. Do not implement the application or create an ADR or skill.

**Requirements reviewed:** Public recipe-name search, recipe and ingredient details, and diet-based chatbot suggestions; Google sign-in, logout, profile, favorites, and a personal calendar with recipe events for registered users.

**Unknowns (clarified by the user):** Project lifetime, team size, platform experience, traffic, and deployment constraints are unspecified. The initial proposals used a small-team/modest-usage scenario for illustration; it is not a confirmed project assumption. Recipe/ingredient data must come from a licensed dataset or external API, but the source is undecided. An LLM is optional: a guided chatbot could suggest recipes using structured diet filters. Notification delivery is not specified; displaying calendar events and sending reminders are separate capabilities to clarify.

## 1. Modular monolith — one backend, separated internal modules

- **Components:** Web UI; one backend with identity/profile, recipe/ingredient search, chatbot, favorites, and calendar modules; one PostgreSQL database. Google and any recipe/AI providers are external integrations.
- **Communication:** Browser → backend over HTTPS; backend modules call each other in-process and access their owned tables. Only the backend calls external providers. Example: adding a favorite checks the session and recipe reference, then inserts a user–recipe link.
- **Advantages:** Simplest deployment and debugging; database transactions keep related changes consistent; low infrastructure cost. Internal boundaries still leave room to extract services later.
- **Disadvantages:** All backend modules deploy together; a slow chatbot can consume resources needed by ordinary requests unless isolated or limited; scaling usually duplicates the whole backend.
- **Concrete difficulties:** Correct Google OIDC callbacks and secure session/logout handling; enforcing ownership on every calendar/favorites request; stable recipe IDs if an external provider changes data; timezone-aware calendar events. Enforce module ownership rather than letting every module freely query every table. Put timeouts and concurrency limits around chatbot calls.

## 2. Domain microservices — independently deployed backends

- **Components:** Web UI and API gateway; identity/profile service, recipe catalog/search service, recommendation/chat service, and personal-data service for favorites/calendars. Each service owns its storage. A message broker is optional, useful if asynchronous reminders are required.
- **Communication:** Browser → gateway → services using HTTPS APIs; recommendation service queries the catalog. Services exchange IDs, not cross-database joins. Optional events such as `ReminderScheduled` go through a broker to a worker.
- **Advantages:** Scale chat separately from search; independent releases and stronger deployment isolation; useful when different teams own distinct domains.
- **Disadvantages:** More hosting, monitoring, deployments, and network failure modes. Independent storage makes cross-domain consistency harder; excessive overhead for a small application. Shared dependencies can still cause cascading failures.
- **Concrete difficulties:** Propagating and validating identity between services; API versioning and distributed tracing; handling catalog outages when displaying favorites; no single transaction across services. If using events, retries can duplicate reminders, so consumers need idempotency keys and deletion/cancellation handling.

## 3. Serverless / backend-as-a-service — managed services plus functions

- **Components:** Static web frontend; managed Google authentication; managed database for profiles, favorites, and calendars; cloud functions for recipe-provider access and chatbot logic. A managed scheduler/queue can deliver reminders if required. One possible ecosystem is Firebase Authentication, Firestore, and Cloud Functions.
- **Communication:** Browser authenticates with the managed provider and accesses personal data under database security rules. Provider secrets stay in functions, invoked over HTTPS. Optional scheduler → function handles reminders.
- **Advantages:** Little server administration; quick initial delivery; automatic scaling and potentially low cost at low usage.
- **Disadvantages:** Provider-specific data models and security rules create lock-in; cold starts and execution limits; usage-based costs can spike. Local testing spans several managed products.
- **Concrete difficulties:** Testing rules so users cannot read others' calendars; designing document indexes and denormalized recipe references; reliable deletion of a calendar and its events (not necessarily automatic). An arbitrary substring recipe-name search may need an external search service/API. Long chatbot requests may exceed function limits, and scheduled invocations may retry, requiring duplicate protection.

## Shared design concerns

- Use structured diet/ingredient constraints to filter real catalog recipes; do not let generated text invent recipe facts or claim allergy safety. Missing ingredient information must be treated explicitly.
- Decide recipe-data sourcing, licensing, quotas, and caching before committing to a search design.
- Keep private calendar/favorite data separate from public recipe browsing and check authorization server-side or through tested database rules.
- Clarify whether reminders mean visible calendar entries, email, or push notifications; delivery adds scheduling, retries, and timezone work to every option.

## Comparison

| Criterion | Modular monolith | Microservices | Serverless / BaaS |
|---|---|---|---|
| Initial development | Simple | Most complex | Fast with provider fit |
| Operations | One backend + database | Many services + infrastructure | Mostly managed |
| Data consistency | Straightforward transactions | Cross-service coordination | Depends on database/model |
| Scaling | Whole backend | Per service | Automatic, within limits |
| Cost at modest usage | Low, fairly predictable | Usually highest baseline | Often low, usage-sensitive |
| Main implementation pain | Auth, ownership, module discipline | Network failures and consistency | Rules, queries, provider limits |
| Best fit | Small team, initial product | Multiple teams or proven scale needs | Rapid delivery using managed services |

## Recommendation and pending feedback

**Recommend a modular monolith** with PostgreSQL and clear module boundaries. It covers all stated stories without distributed-system overhead and keeps calendars/favorites easy to reason about. Keep recipe-data and chatbot integrations behind interfaces so providers can change. Choose serverless instead if minimizing infrastructure management outweighs portability; choose microservices only when measured scaling needs or team boundaries justify them.

**Assistant asks:** Does the modular monolith fit your priorities, or would you prefer managed infrastructure? Should calendar reminders only appear in the app, or also be delivered by email/push?

**Status at end of initial proposals:** Awaiting user feedback. No architecture accepted; no application, ADR, or skill created.

## Follow-up: why not prefer serverless for less administration?

**User:** Leaning toward the modular monolith, but asks why serverless would not be better given reduced server administration; requests concrete implementation/maintenance difficulties and conditions that would change the recommendation.

**Assistant:** Serverless could be better. The initial recommendation prioritizes application simplicity, not a claim that serverless is inferior. Less server administration does not necessarily mean less total maintenance.

### Important distinction

A modular monolith describes code organization; serverless describes how code runs. They are not strict opposites. A modular backend can run on a managed platform or serverless container service with managed PostgreSQL. The earlier serverless proposal specifically combined functions with a Firebase-style document database and direct client access; some difficulties below come from that choice, not serverless itself.

### Modular monolith: concrete work

- **Implementation:** Model recipe/ingredient relationships, favorites, and calendar events in SQL; use migrations and transactions. For example, deleting a calendar and its events can be one transaction with cascading foreign keys. Implement Google sign-in using a maintained library/provider, secure sessions, and ownership checks on every private-data operation. Keep modules from bypassing each other's responsibilities.
- **Maintenance:** Release and roll back the backend, patch dependencies, manage secrets and database connection limits, monitor slow queries and chatbot calls, and test backup restoration. With self-hosting, also maintain the OS, TLS, and database; managed hosting/database remove much of that work, but not application or data responsibility.
- **Pain point:** A slow chatbot can tie up request capacity. Set timeouts and concurrency limits; if necessary, move long jobs to a worker. That worker adds operational work. Whole-backend releases and scaling remain trade-offs.

### Serverless/BaaS: concrete work

- **Implementation:** Managed Google authentication helps, but database rules and function authorization still need cross-user denial tests. In a Firestore-style model, deleting a calendar document does not automatically delete its event subcollection: implement retry-safe cleanup, prevent new events during deletion, and handle partial completion. SQL-backed serverless designs can avoid this particular issue.
- **Search:** Document databases may not support the desired recipe-name matching. An external recipe API may already solve this; otherwise a separate search index adds synchronization and maintenance. Basic name search alone does not necessarily require a separate engine.
- **Chat and reminders:** Check chosen platform limits for request duration, streaming, concurrency, and cold starts. Long calls may need background jobs. Reminder retries need duplicate protection and cancellation checks; these are also required in a monolith using a retrying queue.
- **Maintenance:** Maintain function runtimes/dependencies, security rules, indexes, access policies, quotas, and logs across products. Emulators help but do not prove production permissions or limits. Autoscaling can overload a recipe API or increase AI bills: use rate limits, bounded concurrency, quotas, and cost monitoring. Budget alerts alone do not cap spending. Managed services still need a backup/recovery plan.

### When the recommendation changes

Prefer **serverless/BaaS** when minimizing operations is the main priority, the team already knows the platform, traffic is intermittent, recipe search is covered by an external API, and data/query needs fit its managed database. Validate chatbot execution limits and estimate database/API/AI costs first. A short-lived class demo is also a strong case if no one will operate a backend afterward.

Prefer a **modular monolith** when SQL relationships and transactions, straightforward end-to-end debugging, portability, or longer-running backend work matter more. Team familiarity can outweigh small theoretical architectural advantages.

**Updated recommendation:** Keep modular code boundaries, but do not assume a self-managed server. A managed application host plus managed PostgreSQL is a useful middle ground. For RecipeCove's stated scope, serverless/BaaS is also reasonable; there is no demonstrated scale or query requirement that rules it out. The deciding factors are platform familiarity, data-source/search fit, hosting budget, and who maintains the system after delivery.

**Assistant asks:** Is RecipeCove mainly a short-lived class demo, or intended to remain online? Does the team already know a managed platform such as Firebase?

**Status after serverless follow-up:** Awaiting user response. No final architecture decision, application implementation, ADR, or skill created.

## Follow-up: why PostgreSQL rather than SQLite or MySQL?

**User clarification:** Lifetime, team size, and platform experience must remain unknown. Asked whether any requirement specifically favors PostgreSQL over SQLite or MySQL; requested relevant differences without invented deployment constraints. No accepted decision or ADR.

**Assistant correction:** PostgreSQL was a familiar general-purpose default, not a choice compelled by the brief. The previous small-team, traffic, and lifetime scenarios were conditional examples, not established facts. None of the stated RecipeCove requirements uniquely requires PostgreSQL. All three databases can represent profiles, recipes, ingredients, favorites, calendars, and events, with transactions, unique constraints, and foreign keys.

| Topic | SQLite | PostgreSQL | MySQL |
|---|---|---|---|
| Operation | Embedded database, usually a local file; no separate database server | Separate database service, self-hosted or managed | Separate database service, self-hosted or managed |
| Writes | Writes are serialized: one writer at a time, even with WAL; suitability depends on write frequency and transaction length | Concurrent writing transactions with row-level locking; contention still possible | InnoDB supports concurrent writing transactions with row-level locking; contention still possible |
| Recipe relationships and personal data | Supports the required relational model; enable/verify foreign-key enforcement on each connection | Supports required relationships, constraints, and transactions | InnoDB supports required relationships, constraints, and transactions |
| Recipe-name search | Basic matching and optional FTS5; indexed full-text search is not the same as arbitrary substring matching | Basic matching and built-in full-text search; optional pg_trgm extension for indexed similarity/substring search | Basic matching and InnoDB FULLTEXT indexes; semantics differ from substring matching |
| Calendar time values | No dedicated datetime storage type; choose a consistent text/integer representation | Timestamp types, including timestamp with time zone for instants | DATETIME/TIMESTAMP types with different conversion/range semantics |
| Maintenance | Simpler database setup, but still needs migrations, safe backups, restore tests, and correct file access | Database-service configuration, upgrades, connections, backups and restores; managed hosting can reduce administration | Similar service responsibilities; managed hosting can reduce administration |

### What matters for RecipeCove

- **Favorites and calendar consistency:** All three can enforce a unique user–recipe favorite pair and remove a calendar and its events within a transaction. PostgreSQL is not necessary for these guarantees. SQLite foreign-key enforcement must actually be enabled; use an appropriate transactional engine such as InnoDB with MySQL.
- **Search:** The brief says search by name, without defining exact, prefix, substring, typo-tolerant, or full-text matching. It does not justify a PostgreSQL-specific search feature. If a recipe provider handles search, the local database may not search recipes at all.
- **Calendar dates:** An all-day reminder may only require a date. Timed reminders need an agreed timezone policy in every database. PostgreSQL's timestamp with time zone stores an instant, not the original named timezone; store a zone separately when needed to preserve local-time intent.
- **Concurrency/deployment:** SQLite is a legitimate candidate if its embedded-file model and serialized writes fit the eventual deployment and workload. If independent application instances must share a database, a client-server database is generally easier to arrange; this is a conditional consideration, not a known requirement. Do not reject SQLite based merely on user count.
- **Authentication/chatbot:** Google authentication, ownership checks, external recipe integration, and safe diet suggestions do not select one database over the others.

**Revised position:** A relational database is a reasonable fit, but no database engine is selected. SQLite offers the least database-service administration when its deployment/write model fits. PostgreSQL and MySQL are both reasonable client-server options; existing expertise, hosting support, and demonstrated query needs should decide between them. PostgreSQL's extra features are only advantages if RecipeCove actually needs them. The modular-monolith proposal remains provisional and independent of this choice.

**Assistant asks:** Would you like to examine the search and calendar behavior next, since those may reveal meaningful database requirements?

**Status at end of Task 1:** Awaiting user feedback. No architecture or database decision accepted. No application, ADR, or skill created at that point.

## Task 2 — initial ADR draft

**User:** Start Task 2, write an ADR draft based on the discussion, continue recording notes, and wait for review.

**Assistant actions:** Read `Tasks/Task_2.md` and reviewed the discussion. Created `ADR_001_RecipeCove.md` in `Week_05_Designing/` with status **Draft — proposed for review, not accepted**.

**Draft summary:** Proposes a modular backend with identity/profile, catalog, recommendation/chat, favorites, and calendar boundaries. Includes requirements/context, component table, communication diagram and example flows, comparison with microservices and serverless/BaaS, consequences and concrete implementation difficulties, unresolved choices, and validation/reconsideration criteria. Distinguishes code organization from hosting and document-store limitations from serverless itself.

**Preserved uncertainties:** Lifetime, team size, platform experience, traffic, budget, and deployment constraints remain unknown. No database engine, hosting platform, framework, recipe provider, AI provider, or reminder delivery channel selected. PostgreSQL is explicitly identified as an earlier default rather than a requirement-driven choice. Relational persistence and the modular monolith are proposed, not accepted.

**Review requested:** Is the proposed scope and module structure suitable? Are any sections missing, unnecessary, or unclear? Further revisions will follow the user's review; this is not the final ADR.

**Status after initial draft:** Waiting for user review. Only documentation changed; no application or skill created. No architecture or database decision accepted.

## Task 2 — ADR revision 1: reduce repetition

**User feedback:** Keep draft status at the top, consolidate unresolved choices in their existing section, and shorten the Decision section to architecture, main reasons, and biggest trade-off. Preserve the diagram and implementation difficulties; do not reopen the comparison or introduce technologies.

**Assistant changes to `ADR_001_RecipeCove.md`:** Replaced the Decision text with one paragraph proposing a modular monolith with relational persistence, justified by direct-call debugging and transactional consistency. Explicitly states shared releases, capacity, and failure risks as the biggest trade-off. Removed repeated status/qualification text and moved unknown project constraints and local-catalog storage questions into the unresolved-choices table. Retained the diagram, component responsibilities, flows, implementation difficulties, and existing alternatives comparison without expanding it. Added no technologies.

**Status after revision 1:** Revised draft awaited user review. No decision accepted at that point; no application or skill created.

## Task 2 — final revision and acceptance

**User decision:** Accepted the modular monolith with relational persistence. Requested clarification that adding a favorite derives the user identity from the authenticated session and saves the favorite for that user; users do not need to own public recipes. Requested marking the ADR Accepted and stopping after Task 2 without starting Task 3.

**Assistant changes to `ADR_001_RecipeCove.md`:** Set status to **Accepted**, changed the Decision wording from a proposal to the accepted direction, and clarified the Add favorite flow. The backend validates the authenticated session, derives the user's identity from it, resolves the public recipe reference through the catalog interface, and saves that user's favorite. No recipe ownership requirement applies; the unique user–recipe constraint still prevents duplicates.

**Acceptance scope:** Modular monolith with relational persistence is accepted. Database engine, hosting, and the other choices in the ADR's unresolved section remain open; acceptance does not resolve those choices.

**Final Task 2 outputs:** `ADR_001_RecipeCove.md` (accepted ADR) and `discussion_before.md` (discussion and revision record), both in `Week_05_Designing/`.

**Status:** Task 2 complete. Stopped as requested. Task 3 not started; no application or skill created.

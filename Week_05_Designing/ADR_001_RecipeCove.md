# ADR-001: Proposed modular monolith for RecipeCove

**Status:** Accepted  
**Scope:** Application structure and module responsibilities.

## Context

RecipeCove requires:

- Public recipe-name search, recipe and ingredient details, and a chatbot suggesting recipes for a specified diet.
- Google-account registration/sign-in, logout, and a personal profile.
- Private favorites and calendars, including calendar creation/deletion and recipe-related events.

Sources: [requirements](Tasks/data/RecipeCove.txt), [Task 1 discussion and Task 2 review notes](discussion_before.md), and [Task 2 assignment](Tasks/Task_2.md).

## Decision

Use a **modular monolith with relational persistence**: one backend application with explicit module boundaries, accessed by a web frontend over HTTPS. Direct internal calls simplify debugging, and database transactions keep related personal-data changes consistent without distributed coordination. The biggest trade-off is that modules release together and share backend capacity and failure risks.

### Components and responsibilities

| Component | Responsibility |
|---|---|
| Web frontend | Public browsing/search/chat and authenticated profile, favorites, and calendar screens |
| Identity/profile module | Google sign-in integration, application sessions, logout, and profile access |
| Catalog module | Recipe-name search, recipe/ingredient details, stable recipe references, and recipe-data integration |
| Recommendation/chat module | Collect diet preferences and suggest catalog-backed recipes using structured diet constraints |
| Favorites module | Add, remove, and list favorites belonging to the authenticated user |
| Calendar module | Create/delete owned calendars and add recipe-related events |
| Persistence | Store application-owned user data and recipe references |
| External adapters | Encapsulate Google identity and any selected recipe or AI provider APIs; keep provider secrets server-side |

### Communication overview

```text
Browser / web frontend
          |
        HTTPS
          v
+---------------- One backend application ----------------+
| Identity/profile | Catalog | Recommendation/chat        |
| Favorites        | Calendar                             |
|                                                        |
| Internal module interfaces -> persistence / adapters    |
+--------------------------------------------------------+
          |                              |
  Relational database            Google / recipe provider
                                 / optional AI provider
```

Modules communicate through defined internal interfaces, not network services. Each module owns its writes; other modules request behavior through its interface rather than modifying its tables directly. Database constraints and transactions protect consistency, including unique favorites and calendar/event deletion.

Example flows:

- **Add favorite:** Backend validates the authenticated session and derives the user's identity from it. The favorites module resolves the public recipe reference through the catalog interface and saves the favorite for that user. Users do not need to own the public recipe. A unique constraint prevents duplicate user–recipe favorites.
- **Diet suggestion:** Chat module interprets the diet request, asks the catalog for eligible recipes, and returns suggestions backed by recipe data. An LLM is optional; generated text must not override ingredient constraints or invent recipe facts.
- **Delete calendar:** Backend checks ownership, then deletes the calendar and its events in one transaction. Any future scheduled delivery requires additional cancellation handling.

## Alternatives considered

| Option | Benefits | Concrete difficulties | Assessment |
|---|---|---|---|
| Modular monolith | Direct calls, one backend release, straightforward transactions and tracing | Shared request capacity; whole-backend releases; module boundaries need enforcement | Proposed starting structure |
| Domain microservices | Independent releases and scaling; deployment isolation | Service authentication, API versioning, network failures, tracing, and cross-service consistency | Not selected in this draft: requirements do not establish a need for independent services |
| Serverless/BaaS composition | Less server administration, managed authentication, automatic scaling | Function limits, permissions/security rules, usage costs, and cross-product debugging; document stores may add search and cleanup work | Viable alternative; not ruled out by the brief |

**These options overlap:** modularity is code organization, while serverless is a hosting model. A modular backend may run on managed or serverless infrastructure. Document-database limitations are not inherent to every serverless design.

## Consequences and implementation difficulties

### Expected benefits

- Related personal-data operations can use database transactions without distributed coordination.
- One backend provides a direct path for authorization, debugging, and integration testing.
- Provider adapters and explicit module interfaces limit coupling without introducing service infrastructure.

### Costs and risks

- Backend modules release together and share failure/resource risks. Bound chatbot concurrency and external-call duration so slow providers do not consume all request capacity.
- Secure Google sign-in and logout still require maintained libraries, correct session handling, and server-side ownership checks on every private operation.
- Recipe-provider changes, quotas, licensing, missing ingredient data, and unstable IDs require explicit policies. Do not claim allergy safety from incomplete data or generated suggestions.
- Timed calendar events require correct timezone handling; delivered reminders add scheduling, retries, duplicate protection, and cancellation handling.
- Database migrations, safe backups, restore testing, dependency updates, secrets, and monitoring remain necessary. Managed hosting reduces infrastructure work, not application responsibility.
- Moving modules into services later would still require deliberate API, data-ownership, and consistency work; boundaries do not make extraction automatic.

## Deliberately unresolved choices

| Choice | Current position / evidence needed |
|---|---|
| Project and operating constraints | Lifetime, team size, platform experience, traffic, budget, and deployment constraints are unknown; do not treat illustrative scenarios as confirmed requirements. |
| Database engine | SQLite, PostgreSQL, and MySQL can all meet the stated relational needs. PostgreSQL was an initial default, not a requirement. Select after deployment, write-concurrency, search, and operational needs are known. |
| Hosting | Self-managed, managed application hosting, and serverless remain open; compare operations, limits, recovery, and costs once constraints are known. |
| Recipe data and search | Select a permitted source and decide whether to store a local catalog; clarify exact/prefix/substring/typo-tolerant matching and whether search is local or provider-hosted. |
| Chatbot | Clarify diet rules, missing-data behavior, and whether guided filtering suffices or an LLM is useful. |
| Calendar reminders | Clarify date-only versus timed events and in-app display versus email/push delivery. No scheduler or notification channel is selected. |
| Framework and language | No selection made. |

## Validation and reconsideration

Validate against the choices above. Implementation checks should demonstrate cross-user access denial, duplicate-favorite prevention, atomic calendar deletion, catalog-backed diet suggestions, and bounded external-provider failures, plus search and calendar behavior matching the clarified requirements.

Reconsider the proposal if:

- Confirmed operating constraints and platform fit make a BaaS composition simpler overall.
- Measured load or explicit team/release requirements justify independent services.
- Search, data-source, or chatbot requirements expose constraints unsuitable for the chosen persistence or runtime.


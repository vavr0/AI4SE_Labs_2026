# Requirements Refinement Network

## Goal and design

The tool converts a directory of source texts into one software requirements
specification. It refines requirements; it does not implement the library system
being described. Input filenames are not hard-coded: the loader recursively reads
UTF-8 `.txt` and `.eml` files from the supplied directory.

The implementation is one Python script using LangGraph's `StateGraph`:

```text
load -> extract -> refine -> review -> render
                    ^         |
                    +-- fixes-+
```

Review sends feedback back to refinement at most twice after the initial draft.
Approval or exhaustion of this revision budget routes to deterministic rendering.
Unresolved findings remain visible in the output; reaching the limit is not
reported as approval. Extraction is not repeated during feedback revisions.

| Node | Implementation | Responsibility |
| --- | --- | --- |
| Load | Ordinary Python | Read sources and retain relative filenames. |
| Extract | `gpt-5.6-luna` | Identify source-grounded candidate requirements, ignoring unrelated conversation. |
| Refine | `gpt-6-luna` | Merge duplicates, normalize vocabulary, assign priorities, and explain rejections. |
| Review | `gpt-5.4-nano` | Compare the draft with original sources and request actionable corrections. |
| Render | Ordinary Python | Assign unique IDs and create `requirements.md`. |

These three distinct models are on the assignment's allowed list and support
structured output. They have separate responsibilities rather than generating
three independent specifications. No comparative model-quality benchmark was
performed. The initial extractor choice, `gpt-4.1-nano`, was replaced after the
API reported it retired.

## Data, tracing, and priorities

The graph state contains source texts, candidates, the refined draft, the latest
review, and a revision counter. Pydantic schemas define the model response fields.
Python supplies source filenames and internal `CAND-...` IDs, rather than asking
models to invent them. The reviewer compares candidate meanings against the full
original documents; no generated text is presented as a verified verbatim quote.

Merging combines the candidates' real source references. One compound candidate
may support several distinct requirements. Unknown references are ignored with
warnings, not turned into invented source filenames. Candidates omitted by the
refiner are retained as provisional requirements with a clearly labeled default
Medium priority and a review warning. Conflicting retain/blacklist dispositions
prefer retaining the candidate and flagging the conflict. These repairs prevent
silent loss without falsely claiming that an imperfect draft passed review.

Each successful document extraction is checkpointed atomically in the local,
Git-ignored `.cache/extraction.json`. Reruns reuse completed extractions; source
content, filename, extractor model, prompt, or schema changes invalidate affected
entries. No API keys are cached. Delete this file only when deliberately requesting
fresh extraction. Refinement and review are rerun, not cached.

The priority scale is:
- **High:** essential functionality, safety, compliance, or explicitly high priority.
- **Medium:** important supporting functionality.
- **Low:** a useful enhancement or explicitly optional functionality.

Each priority includes a reason and an Explicit/Inferred basis. A phrase such as
"key requirement" can justify an inferred priority but does not literally assign
High. The reviewer must not demand invented formulas, defaults, or implementation
decisions absent from the sources. Nonblocking source ambiguities belong in its
summary; genuine unresolved conflicts remain visible as review findings.

## Output and assignment coverage

The submission output is `requirements.md`, saved beside the script. The ignored
extraction cache is local runtime data, not a submission deliverable.
It contains unique `REQ-001`-style IDs, names, paragraph explanations, priorities,
priority reasons, source filenames, a blacklist with `BL-001`-style IDs and rejection
reasons, the priority scale, input-document list, and automated review status.
For presentation, the raw review comments were relocated into this report after
generation; all requirement text remains unchanged. Old development JSON outputs
are not read or regenerated and are not required for submission.

- **ANS1, ANS4:** three LLM-invoking nodes with three different models.
- **ANS2:** deterministic loading and rendering nodes.
- **ANS3:** conditional review-to-refinement feedback loop, bounded to two revisions.
- **ANS5:** Python LangGraph implementation.
- **OS1, OS2:** one Markdown specification with deterministic unique IDs.
- **OS3, OS7:** semantic merging, vocabulary normalization, conflict analysis, and review.
- **OS4:** source filenames preserved through merging and displayed per requirement.
- **OS5:** descriptive names and paragraph explanations requested in model prompts.
- **OS6:** priorities, reasons, and an explained scale in the document.
- **OS8:** per-document extraction, candidate-accounting checks, and source-based review.
- **OS9:** conflicting/nonsensical rejections recorded separately with explanations;
  duplicates are merged rather than blacklisted.

## Running the tool

From `Week_04_Requirements/Task_1/`, use a Python environment with:

```bash
python -m pip install langgraph openai python-dotenv pydantic
```

Put the teacher-provided key in the local, Git-ignored `.env` file:

```dotenv
OPENAI_API_KEY=your_teacher_key
```

The script reads only the `.env` beside itself without changing global environment
variables. If the key is missing or blank, it asks through a hidden prompt.
Credentials are not stored in graph state or the generated specification.

Run the full supplied corpus:

```bash
python requirements_agent.py --input data/corpus
```

Optional `--limit 1` processes one document for cheaper debugging. There are no
custom output-path flags, additional models, or full review-history storage.

## Verification and results

Development used Python 3.10.6, LangGraph 1.2.16, OpenAI SDK 3.35.1,
python-dotenv 1.2.4, and Pydantic 2.14.1.

**The full-corpus live run completed with exit code 0**, taking approximately
7 minutes 46 seconds in this single observed run:

- All **20 source documents** were processed and checkpointed.
- Extraction produced **427 candidates**.
- The generated document contains **74 requirements**, numbered `REQ-001` to `REQ-074`.
- Priorities: **20 High, 52 Medium, 2 Low**.
- No requirements were blacklisted; the separate blacklist section is present.
- Review ran initially and after **two feedback revisions**, then stopped at its limit.
- Final automated review status is **Needs attention**, not approval.
- All **14 review-warning/open-question bullets** are retained under Automated review findings below.
- One unmapped candidate, `CAND-0246`, was preserved as provisional `REQ-074`
  (editable canned-report options), rather than silently discarded.

Post-run structural checks confirmed sequential unique IDs, nonempty names and
explanations, a priority/reason for each requirement, the priority-scale and
blacklist sections, and valid source filenames. Per-requirement citations
collectively cover all 20 input documents. The 427 candidates remain cached.
These checks do not prove perfect semantic completeness or absence of duplicates.

The implementation also passed **28 local/mocked checks**, including model
sequencing, feedback limits, tracing, fallback retention, invalid references,
405-candidate bookkeeping, cache recovery/invalidation, Markdown formatting,
key isolation/redaction, and the simplified CLI. No mock output was substituted
for the live-generated submission document.

## Limitations

The generated specification remains a best-effort LLM result. Some requirements
are broad combinations of related capabilities, and provisional `REQ-074` may
overlap other report-customization requirements. Source ambiguities about capacity
metrics, shelf-space estimation, reporting architecture, and retention remain
visible rather than being resolved with invented policies.

The reviewer is not an infallible judge. For example, its final warning questions
whether `CAND-0288` exists, although the saved candidates confirm that it does.
Other findings and the provisional priority are retained for human inspection.
No additional paid runs were made to force approval. The requirements, priorities,
source references, blacklist, and Needs attention status are unchanged. Only the
raw review section was moved here for readability, not discarded or resolved.
Every assignment specification is addressed by a prompt or deterministic mechanism,
but output quality is not claimed to be perfect.

## Automated review findings

The following is the original automated review summary and its 14 findings/open
questions, relocated from the specification. These are model diagnostics, not
teacher feedback or independently verified facts; their limitations are discussed
above. Moving them does not change the failed automated approval.

The draft requirement matrix is largely consistent with the provided conversation threads and the Galecia/SRS and Evergreen reference documents. However, there are a few demonstrable rubric/source mismatches: (1) several candidate IDs referenced in the matrix are not actually included in the candidate list, (2) one item is explicitly described as optional in a source but was assigned High priority, and (3) several requirements claim legacy browser support or other specifics without grounding that the candidate/source combination supports the exact behavior. Other items are largely consistent but remain ambiguous by design (architecture/historical implementation, capacity metric).

- Unresolved candidate/reference mismatch: In requirement “Material volume reporting”, the candidate_ids include CAND-0288, but CAND-0288 does not exist in the provided candidates list (available candidates around this are CAND-0287 and CAND-0288 is present only in candidates as “Report material volume by category and state”; verify presence—currently the mapping in the provided candidate list indicates CAND-0288 exists, but it is not referenced consistently across the draft’s candidate_ids elsewhere; ensure the exact IDs exist and are unique). Correction: audit candidate_ids in every requirement against the provided candidates array and remove/replace any non-existent or mis-typed IDs.
- Priority contradiction: Requirement “Record cleanup and deletion safeguards” marks “Purge scheduling is optional” but the overall requirement is assigned High. While confirmation-before-delete is High-grounded, “purge scheduling is optional” means the scheduling portion cannot be treated as inherently essential. Correction: split into two requirements: (a) deletion confirmation + orphan-safe cleanup as High; (b) scheduled purging (automation) as Medium/Low or optional, or explicitly state scheduling remains optional within the High requirement text.
- Ungrounded/over-specific legacy browser versioning: Requirement “Client access and browser compatibility” asserts IE 6.0+ support and Firefox 2.0+ support as High. While the SRS (early_draft_srs_galecia.txt) states this, the draft later mixes in meeting/interview nuance that some locations use IE 6 and Firefox 2.0. The matrix also assigns High-level emphasis to this interface behavior. Correction: keep the requirement but ensure priority justification is strictly grounded in early_draft_srs_galecia.txt (OE-4/priority), and avoid implying additional behavioral constraints not present in sources (e.g., “legacy browser versions apply if browser access is used” appears in unresolved_issues; align the requirement text so it doesn’t overcommit).
- Unresolved item about “Editable canned report options” uses “Provisional priority: unmapped candidate CAND-0246 retained to prevent omission; review required.” This is not a source-grounded priority claim and conflicts with the instruction to report only demonstrable violations. Correction: either map CAND-0246 to a source-grounded priority statement (or remove “provisional priority” language), and align priority with the source text (evergreen_reference_2009.txt only lists it as missing; it does not establish a priority level).
- Blacklisting/omissions check: The matrix does not explicitly include candidates/requirements for “customizable shelf-space report per date range” as an explicit requirement beyond the side-by-side comparison and date-range filtering being described inside “Shelf-space utilization reporting”. This is not necessarily a violation (date-range filtering is present), but it is incomplete relative to the shelf-space thread which also asks for Q1 vs Q2 and explicitly mentions seasons matter. Correction: ensure “Shelf-space utilization reporting” requirement text explicitly includes date-range filtering at the same level of specificity as the source (e.g., “Q1 vs Q2 / seasonal comparisons”), or add a separate sub-requirement for date-range filtering.
- Branch capacity is not defined: the sources raise item count versus shelf space, physical item count versus a configured limit, and circulation volume versus processing capacity without choosing a metric.
- Shelf-space estimation is unresolved: item dimensions and item count as a proxy are both proposed, with no selected method.
- Reporting architecture is unresolved. Sources require non-disruptive reporting and propose background processing, queuing, read-only replicas, or a reporting database; other technical notes oppose a separately synchronized or denormalized reporting warehouse.
- Historical reporting is required, but the implementation is not settled. Some sources propose a reporting warehouse, while another says a warehouse is only a possible approach and other notes caution against separate synchronized data.
- The access interface remains an alternative between browser-based access and a Windows-compatible client; legacy browser versions apply if browser access is used.
- The cleanup utility for deleting volumes with associated copies and records without items may be automated or manual; the source explicitly leaves this undecided.
- The capacity overview's grouping and filtering approach for approximately 286 locations is suggested but not selected.
- Some source statements specify legally required retention periods generally, while one financial source states that some data must be retained for seven years; the applicable periods depend on state and local requirements.
- Unmapped candidates retained with provisional priorities: CAND-0246.

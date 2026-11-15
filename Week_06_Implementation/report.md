# Week 06 report

## Task 1 — Repository cloning

The coding assistant used its Bash tool to execute the installed Git CLI:

```bash
git clone https://github.com/Neltharion59/AI4SE_Playground.git Week_06_Implementation/AI4SE_Playground
```

The tool gave the assistant access to a shell, the network, and the local filesystem. Git downloaded the repository from GitHub over HTTPS and created the checkout; the assistant did not reconstruct the source code from model output.

- **Source revision:** `b17f75374a6d63f0f245e472bb707e658c1b3cf7`.
- **Verification:** the fresh checkout was clean and contained 13 Python source modules and 13 test files.
- After recording the revision, only the cloned repository's `.git` directory was removed. Its source files can therefore be tracked normally by the coursework repository rather than as an embedded Git repository. The parent Git/Jujutsu metadata was left intact.

Task 1 did not involve installing dependencies, running tests, or calling the course LLM API.

## Task 2 — Repository chunking

`chunk_repository.py` splits nonempty Python source and test files into **100-line windows with 20-line overlap**. Whole lines preserve readable code; overlap retains nearby context at boundaries. This is a simple, deterministic baseline for the small repository, limiting five retrieved chunks to at most 500 lines. It can split classes or methods and does not guarantee their entire context is retained. Git metadata, virtual environments, caches, symlinks, and non-Python files are excluded.

Chunks are stored in `chunks.jsonl`, one JSON object per line, with `id`, `file`, `start_line`, `end_line`, and `text`. Relative paths and line ranges make chunks traceable; JSONL is easy to inspect and load for embedding without a database dependency.

Run from the coursework repository root:

```bash
python3 Week_06_Implementation/chunk_repository.py --repo Week_06_Implementation/AI4SE_Playground --output Week_06_Implementation/chunks.jsonl
python3 -m unittest discover -s Week_06_Implementation -p 'test_chunk_repository.py' -v
```

**Result:** 59 chunks from all 26 nonempty Python files. All 6 chunking tests passed. The generated JSONL was also checked against the source for exact text, complete file coverage, valid line ranges, unique IDs, and the specified overlap. No embeddings or LLM calls were performed.

## Task 3 — Local embeddings and storage

`embed_chunks.py` uses **`sentence-transformers/all-MiniLM-L6-v2`** on CPU, pinned to revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. It produces 384-dimensional vectors without a hosted embedding service or API key. This small general-purpose English model is suitable as an inexpensive baseline for code with English names/comments; code-specific retrieval quality still needs evaluation.

Each embedded input contains the relative file path followed by the chunk text. Because the model accepts 256 tokens per window, longer inputs are tokenized into multiple windows rather than silently truncated. Normalized window vectors are combined using token-count weights and normalized again. This covers the full input, but cannot model relationships across windows as one long-context encoder would.

`embeddings.npz` stores the 59 original chunk records alongside their float32 vector matrix and metadata: model/revision, pooling method, package versions, and input checksum. It loads with `allow_pickle=False`. A compact matrix is sufficient for this small corpus and supports later cosine matching without a vector-database service.

Reproduce from the coursework repository root:

```bash
python3 -m venv Week_06_Implementation/.venv
Week_06_Implementation/.venv/bin/python -m pip install -r Week_06_Implementation/requirements.txt
HF_HUB_DISABLE_XET=1 Week_06_Implementation/.venv/bin/python Week_06_Implementation/embed_chunks.py --chunks Week_06_Implementation/chunks.jsonl --output Week_06_Implementation/embeddings.npz
Week_06_Implementation/.venv/bin/python -m unittest discover -s Week_06_Implementation -p 'test_*.py' -v
```

The initial model download timed out; retrying with Xet disabled succeeded. The model cache and virtual environment are not submission artifacts.

**Result:** all 59 chunks have finite, unit-normalized 384-dimensional embeddings. Stored chunks and the input checksum match `chunks.jsonl`. All 12 chunking/embedding unit tests passed, and a real embedding run also succeeded with `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`. These are not the Playground test results required in Task 5. No teacher API key was read or used.

## Task 4 — Matching relevant chunks

`retrieve_chunks.py` embeds the textual query with the same pinned model and window-pooling method as the stored chunks. It requires locally cached weights. `match_chunks` also accepts a query embedding directly and returns up to **n** complete chunk records with cosine scores.

Vectors are normalized before a matrix–vector dot product, then sorted by descending similarity. Ties retain index order. Exact scanning is appropriate for only 59 vectors; an approximate index or external vector database would add unnecessary complexity. Index format, dimensions, and model/revision compatibility are checked. Similarity scores are not probabilities of correctness.

Example from the coursework repository root:

```bash
Week_06_Implementation/.venv/bin/python Week_06_Implementation/retrieve_chunks.py --index Week_06_Implementation/embeddings.npz --query 'Implement Money.__bool__: return True when the monetary amount is non-zero.' --top-k 5
```

**Result:** the first match was `playground/playground/models.py:1-100` (cosine 0.6356). All 18 chunking/embedding/retrieval unit tests passed, and self-retrieval succeeded for all 59 stored vectors. An offline check formed each of the 10 provided tasks into a query containing its file, class, method, and docstring; all ten top-five result sets included the target method's definition. This measures definition coverage on this small task set, not completeness of all required context or generated-code correctness. No API calls or source modifications were needed.

## Task 5 — RAG code generation and test results

`solve_tasks.py` provides `solve_task(task_text, ...)`: embed the task locally, retrieve exactly five chunks, send the task/context to **`gpt-5.4-nano`**, and insert its structured response into the target method. AST checks preserve signatures, decorators, and code outside that body. Provided tests are not edited. The original chunk/embedding snapshot is intentionally retained rather than re-indexing generated answers.

The default CLI performs preparation only. Live execution requires `--execute`, reads only the explicitly selected Week 6 `.env`, disables SDK retries, and permits at most ten requests. An existing execution log blocks accidental reruns. Regeneration normally requires pristine method stubs and a new, explicitly selected log path. Only the explicit `--replace-existing` flag permits replacing already implemented bodies of the supplied targets.

```bash
Week_06_Implementation/.venv/bin/python Week_06_Implementation/solve_tasks.py --execute
# Run the supplied tests from their project directory:
(cd Week_06_Implementation/AI4SE_Playground/playground && ../../.venv/bin/python -m unittest discover -s tests -v)
```

**First live run:** all 10 tasks were attempted once; 9 method bodies were written. Recorded usage was 39,749 input tokens and 439 output tokens; no price estimate is inferred. [generation_results.json](generation_results.json) records the targets, five retrieved IDs/scores, request status, and usage.

The first supplied-suite run had **481 tests: 478 passed, 1 failed, and 2 errored**. Its full output is preserved in [playground_test_results_initial.txt](playground_test_results_initial.txt).

- `OrderLog.by_status` remained a stub because the response was rejected with `IndentationError`, causing two test errors. A focused regression exposed a recoverable indentation case; normalization was hardened and responses are now retained before validation.
- `InventoryLedger.__contains__` initially followed the manifest's positive-on-hand requirement. The supplied `test_contains_present_even_if_zero_on_hand_after_commit` instead expects membership after stock reaches zero. This conflict caused the assertion failure.

### Authorized repair and final result

The user authorized **two additional API calls** with the same model and explicitly chose the supplied test contract for inventory membership. [repair_tasks.json](repair_tasks.json) records that clarification; the original assignment manifest and tests remain unchanged. Both method bodies were regenerated through the RAG pipeline, not manually implemented. The repair run is recorded separately in [generation_repairs.json](generation_repairs.json).

```bash
Week_06_Implementation/.venv/bin/python Week_06_Implementation/solve_tasks.py --tasks Week_06_Implementation/repair_tasks.json --replace-existing --log Week_06_Implementation/generation_repairs.json --execute
```

**Final result: all 481 supplied tests passed**, with output in [playground_test_results.txt](playground_test_results.txt). All **28 pipeline unit tests** also passed. All ten requested methods are implemented. There were **12 actual API requests in total**, including the two authorized repairs, with no automatic retries.

AST comparison verified that only designated method bodies changed; supplied tests and assignments remained unchanged. The private key is ignored by Git and an exact-value scan found no occurrence in tracked files. Passing these tests is not proof of correctness beyond their coverage, especially given the explicitly resolved description/test conflict.

## Task 6 — Bonus: proposed pipeline

For this repository, prefer **symbol-first retrieval**: the task already identifies the file, class, and method. Load that method, its constructor, referenced helpers/imports, and relevant tests directly. Combine exact-name/text search with embeddings for less obvious dependencies; embedding similarity alone needlessly guesses known locations.

Chunk by AST functions/classes rather than fixed line counts. Select context according to dependencies and a token budget, not a fixed five chunks: simple methods need less context, while cross-module changes may need more. This adds analysis complexity but preserves meaningful code boundaries.

Generate only the target body, retain the response, validate the patch, and run focused tests followed by the full suite. Retry only failed tasks within an explicit budget. Surface requirement/test conflicts for a user decision rather than changing tests. This is a design proposal, not an implemented or benchmarked improvement.

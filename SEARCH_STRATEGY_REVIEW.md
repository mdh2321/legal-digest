# Weekly Digest Search Implementation Plan

## Objective

Implement a deterministic, coverage-aware search pipeline for the weekly digest so that:

- documented SOP and runtime behavior are aligned,
- jurisdiction/topic coverage is measurable and auditable,
- search cost/latency are controlled, and
- selected stories are biased toward primary legal sources.

## Scope

This plan applies to search generation, retrieval, and search-stage observability for:

- `src/config.py`
- `src/news_collector.py`
- `generate_digest.py` (orchestration hooks)
- `run_digest.py` (runtime/CLI hooks)
- `DIGEST_SEARCH_INSTRUCTIONS.md` (SOP alignment)

---

## Phase 1 — Baseline Matrix Alignment (Priority: P0)

### Goal
Use one canonical baseline search matrix in code and docs.

### Changes

1. **Canonical matrix wiring**
   - Update `NewsCollector` to generate baseline queries from:
     - `DIGEST_JURISDICTIONS`
     - `DIGEST_SEARCH_KEYWORDS`
   - Ensure ASEAN is included in runtime collection.

2. **SOP/config consistency check**
   - Add a startup check that logs/validates:
     - number of jurisdictions,
     - number of keywords,
     - expected baseline query count.
   - Fail fast or emit a high-severity warning if mismatch is detected.

3. **Query mode separation**
   - Introduce explicit query modes:
     - `baseline` (matrix only)
     - `expanded` (source-batch enrichment)

### Deliverables

- Refactored baseline query builder in `src/news_collector.py`.
- `generate_digest.py` logging of baseline matrix size.
- Updated `DIGEST_SEARCH_INSTRUCTIONS.md` to reflect implemented behavior and mode names.

### Acceptance Criteria

- Baseline query count equals `len(DIGEST_JURISDICTIONS) * len(DIGEST_SEARCH_KEYWORDS)` every run.
- ASEAN appears in coverage telemetry and candidate summaries.
- No hardcoded jurisdiction loop bypasses baseline matrix config.

---

## Phase 2 — Coverage-Aware Two-Pass Retrieval (Priority: P1)

### Goal
Improve recall and precision with adaptive expansion only where needed.

### Changes

1. **Pass A (primary-source first)**
   - Run baseline matrix with primary-source preference:
     - regulator/government/court-biased query forms.
   - Record hit counts per `(jurisdiction, keyword)` cell.

2. **Coverage gap detection**
   - Define sparse-cell thresholds (e.g., `accepted_stories < N`).
   - Flag underfilled cells after Pass A.

3. **Pass B (targeted expansion)**
   - Only for sparse cells, run enriched source-batch queries:
     - legal publications,
     - law firms,
     - think tanks/associations.
   - Stop expansion when per-cell coverage threshold is met or budget exhausted.

4. **Query budget controls**
   - Add configurable limits:
     - max total queries/run,
     - max expansion queries/cell,
     - optional early-stop on low marginal yield.

### Deliverables

- Two-pass retrieval flow in `NewsCollector.collect_all_stories`.
- Coverage map object persisted for downstream logging/reporting.
- Config knobs for thresholds and budgets in `src/config.py`.

### Acceptance Criteria

- Every run emits cell-level coverage before/after Pass B.
- Expansion is executed only for sparse cells.
- Query volume is bounded by config limits.

---

## Phase 3 — Date Robustness and Parsing Resilience (Priority: P1)

### Goal
Reduce false negatives from strict date extraction.

### Changes

1. **Date extraction enhancements**
   - Extend parser formats:
     - additional ISO/date variants,
     - common abbreviated month formats,
     - optional localized month mappings where feasible.

2. **Metadata fallback path**
   - If snippet/title parsing fails, use structured metadata date fields from search backend result payload (when present).

3. **Date confidence tagging**
   - Track date provenance per story:
     - `snippet`, `title`, `metadata`, `unknown`.
   - Keep strict week filtering, but make rejection reasons explicit in telemetry.

### Deliverables

- Updated date parsing and fallback logic in `src/news_collector.py`.
- Date-source tags on collected stories (or collection metadata).

### Acceptance Criteria

- Fewer “dropped for missing date” rejections in telemetry against a fixed test fixture.
- No inclusion of stories outside target week.

---

## Phase 4 — Telemetry, Auditability, and QA Hooks (Priority: P2)

### Goal
Make search runs observable and reproducible.

### Changes

1. **Run telemetry artifact**
   - Emit `output/search_telemetry_<date>.json` with:
     - query counts by mode/pass,
     - results/query stats,
     - accepted/rejected counts and reasons,
     - coverage by jurisdiction/keyword,
     - top source domains of accepted items.

2. **CLI surfacing**
   - Add concise console summary in `run_digest.py`:
     - baseline coverage,
     - expansion trigger count,
     - major rejection reasons.

3. **Regression harness**
   - Add deterministic fixture-based test for search strategy behavior:
     - matrix count correctness,
     - ASEAN inclusion,
     - pass-B-only-on-sparse-cells behavior,
     - budget enforcement.

### Deliverables

- Telemetry writer utility and JSON schema.
- New/updated tests validating retrieval strategy behavior.

### Acceptance Criteria

- Each run produces a telemetry artifact.
- Strategy regression tests pass in CI/local.

---

## Implementation Backlog (Work Breakdown)

### Workstream A — Query generation

- A1. Add `build_baseline_queries()` from config matrix.
- A2. Add `build_expansion_queries_for_cell(jurisdiction, keyword)`.
- A3. Remove/retire implicit jurisdiction loops not driven by matrix config.

### Workstream B — Retrieval orchestration

- B1. Implement two-pass loop with per-cell counters.
- B2. Add budget gate and early-stop logic.
- B3. Preserve existing dedup behavior and compatibility with downstream modules.

### Workstream C — Date handling

- C1. Expand date patterns and parsing helpers.
- C2. Add metadata date fallback.
- C3. Add rejection reason taxonomy (`no_date`, `out_of_range`, `parse_error`, etc.).

### Workstream D — Observability and testing

- D1. Emit telemetry JSON artifact.
- D2. Add strategy-focused tests with cached/mock results.
- D3. Add smoke check in `test_system.py` or separate strategy test file.

### Workstream E — Documentation and rollout

- E1. Update `DIGEST_SEARCH_INSTRUCTIONS.md` to match final runtime semantics.
- E2. Document new config knobs in `README.md`.
- E3. Provide migration note for any renamed config keys.

---

## Rollout Plan

1. **Release 1 (safe baseline):** Phase 1 only, feature flag expansion off by default.
2. **Release 2 (adaptive retrieval):** Enable Phase 2 in staging; monitor coverage and query count deltas.
3. **Release 3 (parser resilience):** Ship Phase 3 with telemetry comparisons.
4. **Release 4 (full observability):** Ship Phase 4 and enforce strategy tests in CI.

---

## Risks and Mitigations

- **Risk:** Query count growth increases latency/cost.
  - **Mitigation:** hard budget caps + early stop on low yield.

- **Risk:** Overly strict date filtering still drops valid stories.
  - **Mitigation:** metadata fallback + improved parser + reason telemetry.

- **Risk:** Expansion pass introduces source-noise.
  - **Mitigation:** run expansion only for sparse cells and cap expansion queries.

- **Risk:** Docs drift from implementation again.
  - **Mitigation:** startup parity checks + doc update in same PR for strategy changes.

---

## Success Metrics (Tracked Weekly)

- **Coverage:** ≥1 candidate in at least 10 jurisdictions (including ASEAN tracked separately).
- **Topic spread:** ≥5/7 keyword categories represented in candidate pool.
- **Primary-source ratio:** ≥60% of selected stories from regulator/government/court domains.
- **Efficiency:** ≥20% fewer queries than current expanded-everywhere approach at equal output quality.
- **Stability:** candidate volume variance within expected seasonal band.

---

## Definition of Done

This implementation plan is complete when:

1. Matrix-driven baseline search is the runtime default.
2. Two-pass adaptive retrieval is active and budget-controlled.
3. Date fallback and rejection telemetry are in place.
4. Strategy telemetry artifact is emitted every run.
5. Strategy regression tests pass and docs reflect actual behavior.

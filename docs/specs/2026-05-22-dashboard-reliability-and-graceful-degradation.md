# Spec: Dashboard Reliability and Graceful Degradation

Reference process: https://docs.spec-kitty.ai/

## 1. Spec Metadata
- Title: Dashboard Reliability and Graceful Degradation
- Author(s): AEDES Maintainers
- Date: 2026-05-22
- Status: Review
- Related issue(s): TBD
- Related PR(s): TBD

## 2. Problem Statement
The surveillance dashboard depends on multiple upstream sources (CDC, NASA POWER, iNaturalist, and notebook execution). When one source is delayed or unavailable, publication risk increases and reliability can degrade. The project needs a consistent and testable degraded-mode strategy that preserves service continuity while making data freshness and confidence visible to users.

## 3. Scope
### In Scope
- Define standardized fallback behavior for data-fetch and notebook execution failures.
- Add per-source health and freshness metadata to generated outputs.
- Add deployment-time reliability validation checks and rollback criteria.
- Add monitoring/alert thresholds for stale data and failed notebook conversion.

### Out of Scope
- New disease models or new external data-source integrations.
- Full redesign of dashboard UI layout.
- Replacement of current workflow platform (GitHub Actions).

## 4. Requirements
- Functional requirement 1: If one or more data sources fail, pipeline completes with last-known-good data or synthetic fallback where already supported.
- Functional requirement 2: Dashboard must visibly display freshness timestamps and degraded-mode status per data stream.
- Functional requirement 3: Workflow must fail fast only for integrity-critical errors (corrupt outputs, missing required schema).
- Functional requirement 4: Workflow must emit a machine-readable reliability report for each run.
- Non-functional requirement(s):
  - Reliability: Preserve dashboard publish availability for partial upstream outages.
  - Observability: Operators can determine which source failed and why within one run log/reliability report.
  - Maintainability: Rules are centralized in one documented policy file or module.

## 5. Design and Implementation Approach
- Architecture/data flow summary:
  - Add a reliability policy layer to ingestion/execution stages with three modes: normal, degraded, blocked.
  - Generate reliability_report.json with source status, fallback used, freshness, and severity.
  - Inject reliability banner/metadata into generated dashboard index.
- Components/files affected:
  - scripts/fetch_surveillance_data.py
  - scripts/generate_dashboard.py
  - .github/workflows/surveillance-dashboard.yml
  - tests/test_scripts.py
  - tests/test_notebooks.py
  - data/surveillance/ (reliability metadata artifacts)
- Operational considerations:
  - Keep existing schedules.
  - Ensure synthetic fallback is clearly labeled and timestamped.
  - Preserve successful deployment path when only non-critical sources fail.

## 6. Risks and Mitigations
- Risk 1: Silent data quality degradation from fallback overuse.
  - Mitigation: Add stale-data threshold and warning escalation in reliability report and page banner.
- Risk 2: Increased workflow complexity and false negatives.
  - Mitigation: Keep strict severity taxonomy and add unit tests for mode transitions.
- Risk 3: User trust impact if degraded state is unclear.
  - Mitigation: Add explicit per-source status labels and last-updated timestamps in dashboard output.

## 7. Validation Plan
- Tests to add/update:
  - Unit tests for normal/degraded/blocked mode transitions.
  - Contract tests for reliability_report.json schema.
  - Integration test that simulates upstream failure while preserving publish.
- Manual validation:
  - Trigger workflow with mocked failure in one source.
  - Verify dashboard is published with degraded banner and source-level status.
- Monitoring/post-merge checks:
  - Weekly check of degraded-mode frequency.
  - Alert if the same source is degraded for N consecutive runs.

## 8. Constitution Alignment (Required)
Map this spec to each constitutional principle in CHARTER.md.

### Principle 1: Focused Scope and Mission Boundaries
- Alignment: Targets operational reliability of the existing surveillance mission; no expansion into unrelated features.
- Evidence: Scope restricted to ingestion/execution reliability, status visibility, and deploy validation.

### Principle 2: Secure by Default
- Alignment: Reliability metadata excludes secrets and preserves existing credential handling.
- Evidence: Reliability report includes status and timestamps only; no token/API secret logging.

### Principle 3: Accessible by Default
- Alignment: Degraded-state communication uses plain-language labels and non-color-only indicators.
- Evidence: Reliability status rendered as text labels and timestamp fields; accessibility checks added for dashboard changes.

### Principle 4: Self-Correcting Delivery
- Alignment: Pipeline emits explicit health signals and enforces mode-based behavior.
- Evidence: reliability_report.json, mode-transition tests, and alert thresholds provide feedback loop.

### Principle 5: Sustainable and Maintainable Operations
- Alignment: Centralized reliability policy reduces ad hoc incident handling.
- Evidence: Single policy mechanism documented and covered by tests.

### Principle 6: Energy-Conservative Computation
- Alignment: Prevents repeated full reruns from minor upstream faults by allowing controlled degraded publish.
- Evidence: Reduced redundant rerun demand; scheduled cadence remains unchanged.

### Principle 7: Reliable and Resilient Service
- Alignment: Introduces graceful degradation and explicit blocked conditions for integrity failures.
- Evidence: Publish continuity for partial outages plus strict blocking for corrupt/missing required outputs.

## 9. Exception Register (If Needed)
| Principle | Exception | Rationale | Risk | Owner | Expiration Date | Tracking Issue |
|---|---|---|---|---|---|---|
| None currently | N/A | N/A | N/A | N/A | N/A | N/A |

## 10. Rollout and Rollback
- Rollout plan:
  - Phase 1: Add reliability report generation and tests without changing publish rules.
  - Phase 2: Enable degraded-mode publish for non-critical failures.
  - Phase 3: Add dashboard status presentation and operator runbook updates.
- Rollback/containment plan:
  - Toggle to previous publish behavior by disabling policy checks in workflow while keeping report artifact generation.
  - Revert reliability policy changes if false-positive blocked mode appears in production.
- Communication plan:
  - Document reliability statuses in deployment and operations docs.
  - Announce behavior change to maintainers and data users.

## 11. Definition of Done
- [ ] Spec approved.
- [ ] Constitution alignment complete.
- [ ] Reliability report schema implemented.
- [ ] Tests/checks pass.
- [ ] Documentation updated.
- [ ] Post-merge monitoring checks scheduled.

## 12. Measurable Acceptance Criteria
- [ ] Each workflow run emits `data/surveillance/reliability_report.json`.
- [ ] Reliability report contains per-source `status`, `last_success_at`, and `fallback_used` fields.
- [ ] A simulated single-source outage still publishes dashboard artifacts in degraded mode.
- [ ] Integrity-critical failure blocks publish and marks run as blocked mode.
- [ ] Dashboard output includes visible reliability status text and timestamp metadata.

## 13. Deliverables
- Reliability policy implementation in data-fetch/generation pipeline.
- Reliability report schema and generated artifacts.
- Tests for mode transitions and degraded publish behavior.
- Workflow updates and operator notes for rollback/containment.

## 14. PR Slices
1. Slice 1: Add reliability report schema and artifact generation.
2. Slice 2: Add degraded/blocked mode decision logic and tests.
3. Slice 3: Add dashboard reliability status display and docs/runbook updates.

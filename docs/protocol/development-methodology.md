# MyQuant-v2 Development Methodology

## 1. Architectural Principles
- Feature Slice model: `Spec -> Data -> API -> Bridge -> UI`.
- Prefer server-side fetch over client fetch in Dockerized environments to avoid browser/DNS mismatch.
- Enforce clear network boundaries:
  - Bridge runs on local host boundary for external API integration.
  - Backend runs in container network as system-of-record API.
  - Frontend SSR consumes backend through internal network base.
- Treat API contracts as source of truth between slices.
- Add reliability defaults for external IO: timeout, retry, typed errors, deterministic exit codes.

## 2. Feature Workflow
1. Spec
- Define scope, API contracts, data model, acceptance criteria in `docs/specs/`.

2. Scaffold
- Create folders, modules, routes, configs, and baseline tests.

3. Core Logic
- Implement data model, API behavior, bridge flow, UI behavior by slice order.

4. Hardening
- Add timeout/retry/health checks/structured summary logs/clear exit codes.

5. Tests
- Add unit + integration tests first for critical paths and failure modes.

6. Documentation
- Update runbook/spec/checklists and any operational notes.

7. Review & Merge
- Validate DoD, produce test evidence, assess risk/rollback, merge via PR.

### Definition of Done
- Spec and acceptance criteria updated.
- Implementation complete for target slice(s).
- Error handling and hardening rules applied.
- Automated tests added/updated and passing.
- Operational docs/runbook updated.
- PR includes risk + rollback plan.

### Testing Pyramid Model
- Unit tests: pure logic, serializers, mapping, query building, exit-code behavior.
- Integration tests: API endpoints, DB transactions, auth, bridge-to-backend boundaries.
- E2E tests: representative user and operations flows (search/detail/sync).

## 3. Versioning & Branch Strategy
- Branches:
  - `main`: stable production-ready.
  - `feat/*`: new features.
  - `fix/*`: bug fixes.
  - `refactor/*`: structural changes without behavior change.
- Commit style: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Semantic versioning:
  - MAJOR: breaking API/contract changes.
  - MINOR: backward-compatible features.
  - PATCH: backward-compatible fixes/hardening.

## 4. Refactoring Policy
- Do not mix refactor and feature behavior changes in one PR.
- Require baseline tests before major structural change.
- Preserve external behavior unless explicitly approved in spec/ADR.
- Run regression checks for query performance and API latency where relevant.
- Track risky refactors in ADR if architectural tradeoff is involved.

## 5. Skill & Automation Model
### Core Skills
- Bridge Sync Skill
  - Token/list/upsert flow, retries, health checks, summaries, exit-code conventions.
- Docker Networking Skill
  - Internal vs external hostnames, SSR fetch base, compose diagnostics.
- API Contract Skill
  - Schema-first endpoint behavior, filter semantics, pagination/order guarantees.
- Hardening Skill
  - Timeout/retry/backoff, error taxonomy, observability, safe defaults.

### Automation Examples
- Daily dry-run sync
  - Run bridge dry-run with verbose summary and alert on unusual quality ratios.
- Weekly full sync
  - Execute real sync, capture inserted/updated/unchanged counts.
- Nightly test suite
  - Run backend and bridge test suites; report failures and flaky patterns.

## 6. Documentation Governance
- `docs/specs/`: feature-level contracts and MVP/phase specs.
- `docs/adr/`: architectural decision records and long-term tradeoffs.
- `docs/runbooks/`: operational procedures, troubleshooting, incident actions.
- `docs/protocol/`: engineering standards, checklists, prompt templates.

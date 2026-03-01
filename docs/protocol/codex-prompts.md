# Codex Prompt Templates

### Feature Scaffold Prompt
```md
Implement [feature-name] in MyQuant-v2.

Scope:
- Spec file: [path]
- Layers: [Data/API/Bridge/UI]
- Non-goals: [list]

Requirements:
1) Scaffold files and routes.
2) Implement minimal working behavior per spec.
3) Add baseline tests.
4) Keep changes isolated to requested scope.

After changes:
- Show modified files.
- Show test commands and results.
```

### Hardening Prompt
```md
Harden [module/flow] for production reliability.

Add:
- Timeout and retry policy
- Health checks
- Deterministic exit codes
- User-friendly errors (no tracebacks)
- Structured summary logs

Do not change business behavior.
Return key diffs and validation output.
```

### Testing Prompt
```md
Add tests for [component/endpoint/flow].

Cover:
- Happy path
- Validation failures
- Network failure/timeouts
- Regression edge cases

Use lightweight fixtures/factories and avoid external network.
Show exact pytest commands and summary.
```

### Refactor Prompt
```md
Refactor [target] for [goal: readability/performance/maintainability].

Rules:
- No feature behavior change
- Keep public contracts intact
- Add/adjust tests to prove parity
- Call out any performance tradeoffs

After changes:
- Provide before/after architecture summary
- Provide risk and rollback notes
```

### Automation Prompt
```md
Create an automation for [task].

Include:
- Schedule intent (daily/weekly/nightly)
- Scope (workspaces/services)
- Output format and destination
- Guardrails (skip if condition, fail-safe behavior)

Return suggested automation config and verification steps.
```

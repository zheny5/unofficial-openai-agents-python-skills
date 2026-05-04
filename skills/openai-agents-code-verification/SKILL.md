---
name: openai-agents-code-verification
description: "INVOKE THIS SKILL when you need to choose and run the verification stack after changing OpenAI Agents SDK Python code, tests, or skill guidance. Use it to keep validation ordered, fast-failing, and tied to the actual change surface."
---

# OpenAI Agents Code Verification

<overview>
Use this skill after code or skill edits. Run the smallest trustworthy checks first, then expand to the repo's canonical verification stack. Do not mark a change done until syntax, focused tests, deterministic validation, and the relevant evals or full suite have been checked.
</overview>

<verification-order>

1. Syntax and import sanity for touched Python files.
2. Targeted unit or smoke tests for the change surface.
3. Repo-specific evals or validation harnesses.
4. The full verification stack if the change is runtime-sensitive.

</verification-order>

<repo-pattern>

For this repository, the canonical checks are:

- `python3 -m py_compile ...`
- `python3 evals/run_static_eval.py --format markdown` for static eval coverage
- `python3 evals/run_live_eval.py --agent claude --dry-run --format markdown` for live eval prompt coverage
- `git diff --check`
- `make format`, then `make lint`, `make typecheck`, and `make tests` when working in the official SDK repo

</repo-pattern>

<decision-rules>

- Fail fast: stop at the first real failure and fix that first.
- Prefer the narrowest command that proves the surface.
- If a validation command rewrites files, treat it as implementation, not verification.
- If the change touched runtime behavior, rerun the relevant checks after fixing issues.
- If the change touched source-backed skill guidance, validate the source map and expected terms too.

</decision-rules>

<testing-debugging-pattern>

Verification should prove the changed boundary:

- Smoke test imports and simple execution before broad test runs.
- Validate tool behavior, structured outputs, schemas, and deterministic artifacts directly.
- Add or run negative tests for failure handling when the change touches guardrails, sessions, streaming, or providers.
- Keep debug output actionable: command, return code, trace or request ID, failing path, and source map entry.

</testing-debugging-pattern>

<example>

```python
VERIFY_STEPS = [
    ["python3", "-m", "py_compile", "evals/run_static_eval.py", "evals/run_live_eval.py"],
    ["python3", "evals/run_static_eval.py", "--format", "markdown"],
    ["python3", "evals/run_live_eval.py", "--agent", "claude", "--dry-run", "--format", "markdown"],
    ["git", "diff", "--check"],
]
```

</example>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Running the full suite before a cheap sanity check | Start with syntax and focused tests |
| Treating eval output as a substitute for verification | Use both evals and real checks |
| Letting one failure hide later failures | Stop, fix, and rerun the sequence |
| Skipping diff hygiene | Run `git diff --check` before commit |
| Ignoring source-backed drift | Recheck the source map before changing API examples |

</common-mistakes>

<notes>
- Adapt the exact commands to the target repo, but keep the order.
- For runtime-sensitive changes, verification is part of the implementation, not an optional follow-up.
</notes>

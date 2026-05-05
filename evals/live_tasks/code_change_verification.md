# Live Task: Code Change Verification

Write a compact Python helper or script that lists the verification steps you would run after changing OpenAI Agents SDK Python code.

It should include:

- syntax or import checks
- targeted tests or smoke checks
- repo-specific evals
- a fail-fast order

Return exactly one valid Python code block. The code should define only an ordered list of shell commands or steps. Do not include complex subprocess logic.

The Python code must include these literal command strings:

- `python3 -m py_compile`
- `python3 evals/run_static_eval.py --format markdown`
- `python3 evals/run_live_eval.py --agent claude --dry-run --format markdown`
- `git diff --check`
- `make format`
- `make lint`
- `make typecheck`
- `make tests`

Include comments or labels containing the literal phrases `fail fast`, `verification stack`, `smoke`, and `source map`.

Keep the code parseable with `ast.parse`; prefer simple string literals.
Include the literal phrase `static eval` in a comment or label, not only in the command string.
Include the literal phrase `live eval` in a comment or label, not only in the command string.

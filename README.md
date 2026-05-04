# OpenAI Agents Python Skills

Reusable Agent Skills for coding agents that write or review projects built with
the OpenAI Agents SDK for Python.

These skills are modeled after the LangChain coding-agent skills style: compact
trigger metadata, high-signal implementation guidance, short examples, and
explicit fixes for common mistakes.

## Evaluation

This repo uses three layers of checks:

- `python3 evals/run_static_eval.py --format markdown` checks skill coverage, trigger quality, and source-map drift.
- `python3 evals/run_live_eval.py --agent claude --dry-run --format markdown` checks forward-test prompt coverage for coding agents.
- `python3 evals/run_runtime_eval.py --format markdown` runs the official SDK runtime with the official repo's `FakeModel`, proving `Agent` and `Runner` behavior without an API key.

## Skills

- `openai-agents-core` - agents, runner usage, run results, context, and basic lifecycle.
- `openai-agents-tools` - `@function_tool`, tool boundaries, schemas, and error handling.
- `openai-agents-models` - model selection, OpenAI-compatible clients, model settings, and provider wiring.
- `openai-agents-structured-output` - Pydantic outputs, validation, and machine-readable artifacts.
- `openai-agents-handoffs` - multi-agent handoffs and routing design.
- `openai-agents-guardrails` - input/output guardrails and policy checks.
- `openai-agents-sessions-tracing` - sessions, tracing, streaming, and debugging.
- `openai-agents-implementation-strategy` - compatibility boundaries, release gates, and rewrite vs shim decisions.
- `openai-agents-runtime-probe` - local/live runtime probes, case matrices, and failure/repetition analysis.
- `openai-agents-code-verification` - ordered verification stacks and fail-fast checks after code changes.
- `openai-agents-docs-sync` - source-backed docs and skill drift correction against the official repo.

## Install

Install all skills with a compatible Agent Skills CLI:

```bash
npx skills add zheny5/openai-agents-python-skills --skill '*' --yes --global
```

Install for a specific agent:

```bash
npx skills add zheny5/openai-agents-python-skills --agent codex --skill '*' --yes --global
npx skills add zheny5/openai-agents-python-skills --agent claude-code --skill '*' --yes --global
```

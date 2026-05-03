# OpenAI Agents Python Source Map

Source checkout used for calibration:

- Local path: `/home/yuzheng/projects/openai-agents-python`
- Observed commit: `f2fb9ff`
- Official docs: `https://openai.github.io/openai-agents-python/`

Use this map before changing any SDK API examples in `skills/**/SKILL.md`.

## Skill To Source Mapping

| Skill | Source/docs to inspect | Key symbols/patterns |
| --- | --- | --- |
| `openai-agents-core` | `examples/basic/hello_world.py`, `src/agents/run.py`, `src/agents/result.py` | `Agent`, `Runner.run`, `Runner.run_sync`, `Runner.run_streamed`, `final_output`, `RunConfig` |
| `openai-agents-tools` | `examples/basic/tools.py`, `src/agents/tool.py` | `function_tool`, Pydantic tool return values, typed parameters, tool docstrings |
| `openai-agents-models` | `examples/model_providers/custom_example_agent.py`, `examples/model_providers/custom_example_provider.py` | `AsyncOpenAI`, `OpenAIChatCompletionsModel`, `OpenAIProvider`, `set_tracing_disabled`, `RunConfig(model_provider=...)` |
| `openai-agents-structured-output` | `examples/research_bot/agents/planner_agent.py`, `examples/basic/non_strict_output_type.py`, `src/agents/agent_output.py` | `output_type=BaseModel`, `AgentOutputSchema`, `strict_json_schema=False`, `final_output`, `final_output_as(...)` |
| `openai-agents-handoffs` | `examples/agent_patterns/routing.py`, `examples/handoffs/message_filter.py`, `src/agents/handoffs/` | `handoffs=[...]`, `result.current_agent`, `trace(...)`, `HandoffInputData` |
| `openai-agents-guardrails` | `examples/agent_patterns/input_guardrails.py`, `examples/agent_patterns/output_guardrails.py`, `tests/test_guardrails.py` | `input_guardrail`, `output_guardrail`, `GuardrailFunctionOutput`, `InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered`, `output_info` |
| `openai-agents-sessions-tracing` | `examples/basic/stream_text.py`, `examples/agent_patterns/routing.py`, `examples/memory/sqlite_session_example.py`, `src/agents/tracing/` | `Runner.run_streamed`, `stream_events`, `trace`, `SQLiteSession`, `session=` |

## Calibration Rules

- For API examples, verify imports and call signatures against the source map before editing.
- For structured outputs, prefer Pydantic `BaseModel` with `output_type`; use `AgentOutputSchema(..., strict_json_schema=False)` only for schemas that are not strict-compatible.
- For custom model endpoints, use `from openai import AsyncOpenAI` and `OpenAIChatCompletionsModel(..., openai_client=client)`.
- For guardrails, return `GuardrailFunctionOutput(output_info=..., tripwire_triggered=...)` and test tripwire exception paths.
- For routing, validate selected specialist or `result.current_agent`; do not rely only on final prose.


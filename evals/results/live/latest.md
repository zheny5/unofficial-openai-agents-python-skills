# Live Eval Report

Generated: `2026-05-05T13:48:22.529014+00:00`
Agent: `codex`
Dry run: `False`

## Tasks

- `minimal_agent_tool_output`: combined `0.0`, text `0.0`, code `0.0`, returncode `None`
  Python code blocks: 0
  Missing expected: Agent, Runner.run, function_tool, BaseModel, output_type, final_output
  Missing architecture: tool, typed, validate, test
- `custom_model_provider`: combined `0.0`, text `0.0`, code `0.0`, returncode `None`
  Python code blocks: 0
  Missing expected: AsyncOpenAI, OpenAIChatCompletionsModel, ModelProvider, RunConfig, model_provider, set_tracing_disabled
  Missing architecture: tool-calling smoke test, structured-output, fallback, sanitized
- `sessions_tracing_streaming`: combined `0.0`, text `0.0`, code `0.0`, returncode `None`
  Python code blocks: 0
  Missing expected: Runner.run_streamed, stream_events, SQLiteSession, trace, group_id, session=
  Missing architecture: secret, request ID, final, failure
- `runtime_behavior_probe`: combined `0.0`, text `0.0`, code `0.0`, returncode `None`
  Python code blocks: 0
  Missing expected: case_id, scenario, mode, question, setup, result_flag, evidence
  Missing architecture: repeat-3, warm-up, control, cleanup
- `code_change_verification`: combined `0.0`, text `0.0`, code `0.0`, returncode `None`
  Python code blocks: 0
  Missing expected: py_compile, static eval, live eval, git diff --check, make format, make lint, make typecheck, make tests
  Missing architecture: fail fast, verification stack, smoke, source map
- `provider_integration_module`: combined `0.0`, text `0.0`, code `0.0`, returncode `1`
  Python code blocks: 0
  Missing expected: AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider, set_tracing_disabled, provider-test-key
  Missing architecture: tool-calling smoke test, structured-output, sanitized, request ID
- `trace_guided_bugfix`: combined `0.0`, text `0.0`, code `0.0`, returncode `1`
  Python code blocks: 0
  Missing expected: request_id, trace, group_id, final_output, session=
  Missing architecture: failure, reproduce, validate, secret

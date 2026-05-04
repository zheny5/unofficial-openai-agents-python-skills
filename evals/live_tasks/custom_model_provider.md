# Live Task: Custom Model Provider

Write a source-accurate OpenAI Agents SDK Python example for a self-hosted
OpenAI-compatible model endpoint.

Include both:

- agent-level model wiring with `OpenAIChatCompletionsModel`
- run-level model routing with a `ModelProvider` and `RunConfig(model_provider=...)`

Add brief smoke-test guidance for tool calling, structured output, fallback behavior,
sanitized provider failures, and tracing when the key is not an OpenAI platform key.
The code should explicitly mention `set_tracing_disabled` or an equivalent tracing-suppression step.

The Python code must include these literal names:

- `AsyncOpenAI`
- `OpenAIChatCompletionsModel`
- `ModelProvider`
- `RunConfig`
- `set_tracing_disabled`

The code must also include the literal phrases `tool-calling smoke test` and `structured-output`.
The credential example must use an environment variable or a neutral placeholder like `provider-test-key`; do not use any `sk-...` value.

Return exactly one valid Python code block. Include smoke-test guidance as Python comments or string constants inside the code block.

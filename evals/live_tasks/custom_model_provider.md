# Live Task: Custom Model Provider

Write a source-accurate OpenAI Agents SDK Python example for a self-hosted
OpenAI-compatible model endpoint.

Include both:

- agent-level model wiring with `OpenAIChatCompletionsModel`
- run-level model routing with a `ModelProvider` and `RunConfig(model_provider=...)`

Add brief smoke-test guidance for tool calling, structured output, fallback behavior,
sanitized provider failures, and tracing when the key is not an OpenAI platform key.


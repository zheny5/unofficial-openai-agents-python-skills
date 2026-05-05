# Live Task: Provider Integration Module

Write a compact OpenAI Agents SDK Python provider module for a self-hosted
OpenAI-compatible endpoint.

It must include:

- a reusable provider factory
- `AsyncOpenAI`
- `OpenAIChatCompletionsModel`
- `ModelProvider`
- `RunConfig`
- `set_tracing_disabled`
- a `tool-calling smoke test`
- a `structured-output` smoke test
- a neutral credential placeholder like `provider-test-key`
- a sanitized failure note
- a `request ID` in logs or comments

Return exactly one valid Python code block.
Include the literal phrases `tool-calling smoke test`, `structured-output`, `sanitized`, and `request ID` in comments or string constants.

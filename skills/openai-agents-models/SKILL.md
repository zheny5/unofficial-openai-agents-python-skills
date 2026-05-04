---
name: openai-agents-models
description: "INVOKE THIS SKILL when configuring models, model providers, OpenAI-compatible endpoints, LiteLLM adapters, or model settings in an OpenAI Agents SDK Python app."
---

# OpenAI Agents Models

<overview>
Model configuration can be set on an `Agent`, overridden per run with `RunConfig`, or supplied through a provider/client. Keep provider wiring centralized so business agents do not hardcode endpoint details.
</overview>

<when-to-use>

| Scenario | Pattern |
| --- | --- |
| Standard OpenAI model | Set `Agent(model="...")` |
| Per-request model override | Use `RunConfig(model=...)` |
| OpenAI-compatible custom endpoint | Configure an OpenAI-compatible async client/model provider |
| Multiple providers | Centralize provider creation in one module |
| Model behavior tuning | Use model settings, not prompt hacks |

</when-to-use>

<simple-model>

```python
from agents import Agent

agent = Agent(
    name="planner",
    model="gpt-4.1",
    instructions="Create concise implementation plans.",
)
```

</simple-model>

<run-override-pattern>

Use run-level overrides for experiments, tests, or tenant-specific routing. Do not scatter model strings through tools.

```python
from agents import Agent, Runner, RunConfig

agent = Agent(name="assistant", instructions="Answer accurately.")

result = Runner.run_sync(
    agent,
    "Draft a short release note.",
    run_config=RunConfig(model="gpt-4.1-mini"),
)
```

</run-override-pattern>

<openai-compatible-pattern>

When using a self-hosted or third-party OpenAI-compatible endpoint, keep the client setup in infrastructure code and pass the resulting model/provider into agents or run config. Many providers support Chat Completions before they support Responses, so `OpenAIChatCompletionsModel` is commonly the right compatibility path.

```python
import os

from openai import AsyncOpenAI
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(
    api_key=os.environ["PROVIDER_API_KEY"],
    base_url="https://your-openai-compatible-endpoint/v1",
)

model = OpenAIChatCompletionsModel(
    model="your-model-name",
    openai_client=client,
)

agent = Agent(
    name="custom-model-agent",
    instructions="Use tools when needed and produce validated outputs.",
    model=model,
)
```

Disable or reconfigure tracing if you are not using an OpenAI platform API key for traces.
If you need a placeholder for docs or tests, use a neutral value such as `"provider-test-key"`, never an OpenAI-looking `sk-...` string.

</openai-compatible-pattern>

<model-settings-pattern>

Use `ModelSettings` for model behavior knobs instead of burying them in prompts.

```python
from agents import Agent, ModelSettings

agent = Agent(
    name="classifier",
    model="gpt-4.1-mini",
    model_settings=ModelSettings(temperature=0.1),
    instructions="Classify the request into the provided categories.",
)
```

</model-settings-pattern>

<custom-provider-pattern>

Use a `ModelProvider` when provider selection belongs in `RunConfig`, not one fixed agent.

```python
import os

from openai import AsyncOpenAI
from agents import Model, ModelProvider, OpenAIChatCompletionsModel, RunConfig, Runner

client = AsyncOpenAI(
    api_key=os.environ["PROVIDER_API_KEY"],
    base_url="https://your-openai-compatible-endpoint/v1",
)

class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(
            model=model_name or "your-model-name",
            openai_client=client,
        )

result = await Runner.run(
    agent,
    "Run a provider smoke test.",
    run_config=RunConfig(model_provider=CustomModelProvider()),
)
```

</custom-provider-pattern>

<model-testing-debugging-pattern>

Treat each non-default provider as a dependency with explicit smoke tests.

| Scenario | Check |
| --- | --- |
| Tool-calling smoke test | A tiny `@function_tool` is called with typed arguments |
| Structured-output schema test | `output_type` returns a typed object, not raw JSON text |
| Negative capability test | Unsupported tools or schemas fail with a clear error |
| Provider failure debug | Log base URL, model name, request ID, and sanitized error category |
| Tracing behavior | Disable tracing or set a tracing export key when not using an OpenAI platform key |

Provider modules should expose both a `tool-calling smoke test` and a `structured-output` smoke test so coding agents have a stable template to copy.

Keep retries, latency budgets, fallback model selection, schema validation, and deterministic repair outside prompts.

</model-testing-debugging-pattern>

<model-readiness-checklist>

- Tool calling works for your target model.
- Structured output works if you set `output_type`.
- Long-context behavior is tested with realistic inputs.
- Streaming events are tested if the UI depends on streaming.
- Latency and retry policy are owned outside prompts.
- Fallback model behavior is explicit; do not silently downgrade critical tasks.

</model-readiness-checklist>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Assuming every OpenAI-compatible model supports tools | Run a tool-calling smoke test |
| Hardcoding model names inside agents, tests, and tools | Centralize defaults and allow `RunConfig` override |
| Using prompts to compensate for unsupported structured output | Use a compatible model or validate/repair deterministically |
| Mixing provider auth into agent instructions | Keep credentials in environment/config only |
| Using `sk-...` as a fake third-party key in examples | Use env vars or a neutral placeholder like `provider-test-key` |
| Migrating model strings without checking behavior | Re-run tool, structured output, and guardrail tests |
| Debug logs expose provider secrets | Log sanitized base URL/model/request IDs, never API keys |
| Fallback silently changes capabilities | Test fallback models against the same tool and schema requirements |

</common-mistakes>

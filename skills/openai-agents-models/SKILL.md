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
from openai import AsyncOpenAI
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(
    api_key="YOUR_PROVIDER_API_KEY",
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
| Migrating model strings without checking behavior | Re-run tool, structured output, and guardrail tests |

</common-mistakes>

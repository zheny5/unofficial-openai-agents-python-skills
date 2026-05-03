---
name: openai-agents-core
description: "INVOKE THIS SKILL when writing or reviewing ANY OpenAI Agents SDK Python application. Covers Agent, Runner, RunConfig, context, streaming entrypoints, result handling, and core architecture."
---

# OpenAI Agents Core

<overview>
The OpenAI Agents SDK for Python builds agentic apps from a few primitives:

- **Agent**: instructions, model configuration, tools, output type, handoffs, hooks.
- **Runner**: executes agents with `run`, `run_sync`, or `run_streamed`.
- **Run result**: inspect `final_output`, generated items, handoff state, and guardrail outcomes.
- **Context**: application state passed to tools, hooks, handoffs, and guardrails.
- **RunConfig**: per-run overrides for model, provider, tracing, and related settings.

Keep deterministic business logic outside the agent. Use agents for language reasoning and routing; use tools and typed code for side effects.
</overview>

<when-to-use>

| Need | Use |
| --- | --- |
| One agent with tools and instructions | `Agent(...)` + `Runner.run(...)` |
| Synchronous CLI/script prototype | `Runner.run_sync(...)` |
| Async service or web backend | `await Runner.run(...)` |
| Partial events or live UI | `Runner.run_streamed(...)` |
| Per-request state | `context` / `RunContextWrapper` |
| Per-run model or tracing override | `RunConfig` |

</when-to-use>

<basic-agent>

```python
from agents import Agent, Runner

agent = Agent(
    name="assistant",
    instructions="Answer concisely and ask for missing required inputs.",
)

result = Runner.run_sync(agent, "Summarize the tradeoffs of tool calling.")
print(result.final_output)
```

</basic-agent>

<async-service-pattern>

```python
from agents import Agent, Runner

support_agent = Agent(
    name="support",
    instructions="Resolve the user's issue using available tools.",
)

async def handle_message(message: str) -> str:
    result = await Runner.run(support_agent, message)
    return result.final_output
```

</async-service-pattern>

<context-pattern>

Use context for request-scoped application state, not for long documents that should live in files, databases, or retrieval systems.

```python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper, Runner, function_tool

@dataclass
class AppContext:
    user_id: str
    workspace_id: str

@function_tool
def current_workspace(ctx: RunContextWrapper[AppContext]) -> str:
    return ctx.context.workspace_id

agent = Agent[AppContext](
    name="workspace-agent",
    instructions="Use tools when workspace-specific data is needed.",
    tools=[current_workspace],
)

result = Runner.run_sync(
    agent,
    "Which workspace am I in?",
    context=AppContext(user_id="u_123", workspace_id="w_456"),
)
```

</context-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Putting API calls or filesystem writes in instructions | Wrap them as explicit tools |
| Passing huge documents directly as one prompt | Store externally; pass references or normalized extracts |
| Using `run_sync` in an async web route | Use `await Runner.run(...)` |
| Treating `final_output` as validated JSON | Use `output_type` and Pydantic for structured outputs |
| Letting one giant agent do every job | Split deterministic steps into Python functions; use handoffs only for real specialization |

</common-mistakes>

<design-rule>
For production workflows, design the outer workflow first, then insert agent steps where language reasoning is actually needed.
</design-rule>


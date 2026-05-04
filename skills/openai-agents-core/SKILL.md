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

<typed-output-pattern>

When downstream code depends on the result, make the wrapper typed and validate the final output directly.

```python
from pydantic import BaseModel
from agents import Agent, Runner, function_tool

class SearchResult(BaseModel):
    title: str
    url: str

@function_tool
def lookup_docs(query: str) -> str:
    """Return a deterministic search result stub."""
    return f"https://example.invalid/search?q={query}"

agent = Agent(
    name="searcher",
    instructions="Use the tool and return a typed result.",
    tools=[lookup_docs],
    output_type=SearchResult,
)

async def run_search(query: str) -> SearchResult:
    result = await Runner.run(agent, f"Search for {query}")
    typed_output: SearchResult = result.final_output
    return typed_output
```

</typed-output-pattern>

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

<testing-debugging-pattern>

Wrap runner calls in small functions so tests can assert behavior without duplicating agent setup. Preserve enough debug context to reproduce failures, but keep secrets and full private documents out of logs.

```python
from agents import Agent, Runner, RunConfig

agent = Agent(
    name="assistant",
    instructions="Answer concisely. Use tools only when needed.",
)

def answer_once(prompt: str, *, model: str = "gpt-4.1-mini") -> str:
    result = Runner.run_sync(
        agent,
        prompt,
        run_config=RunConfig(model=model),
    )
    return result.final_output

def test_answer_once_smoke() -> None:
    output = answer_once("Say hello in three words or fewer.")
    assert isinstance(output, str)
    assert output.strip()
```

If the wrapper returns structured output, validate the typed `final_output` explicitly:

```python
async def test_run_search_returns_typed_output() -> None:
    result = await run_search("openai agents")
    assert isinstance(result, SearchResult)
    assert result.title
    assert result.url.startswith("https://")
```

| Scenario | Check |
| --- | --- |
| Minimal successful run | Test the wrapper returns non-empty `final_output` |
| Typed structured output | Validate the typed `final_output` with `assert isinstance(...)` |
| Tool-free smoke test | Use a prompt that should not require IO or side effects |
| Expected failure/debug case | Preserve request ID, model, prompt version, and input reference |
| Async entrypoint | Test `await Runner.run(...)` instead of calling `run_sync` inside async code |

For failed runs, inspect trace/debug output and generated items before changing prompts. Do not hide retries, validation, or failure handling in agent instructions.

</testing-debugging-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Putting API calls or filesystem writes in instructions | Wrap them as explicit tools |
| Passing huge documents directly as one prompt | Store externally; pass references or normalized extracts |
| Using `run_sync` in an async web route | Use `await Runner.run(...)` |
| Treating `final_output` as validated JSON | Use `output_type` and Pydantic for structured outputs |
| Letting one giant agent do every job | Split deterministic steps into Python functions; use handoffs only for real specialization |
| Debugging only from final text | Inspect traces, generated items, and validation failure context |
| Tests call raw `Runner.run_sync` everywhere | Wrap runs in app functions and test those boundaries |

</common-mistakes>

<design-rule>
For production workflows, design the outer workflow first, then insert agent steps where language reasoning is actually needed.
</design-rule>

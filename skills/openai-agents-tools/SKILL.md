---
name: openai-agents-tools
description: "INVOKE THIS SKILL when adding, modifying, or debugging tools in an OpenAI Agents SDK Python app. Covers function_tool, tool schemas, context-aware tools, side effects, and safe tool design."
---

# OpenAI Agents Tools

<overview>
Tools are the boundary between model reasoning and deterministic code. Keep tools small, typed, and explicit. A good tool does one side-effectful or data-fetching operation and returns a compact, useful result.
</overview>

<tool-selection>

| Need | Pattern |
| --- | --- |
| Simple Python function as a tool | `@function_tool` |
| Tool needs request/user state | Add `RunContextWrapper[ContextType]` as first arg |
| Tool has side effects | Make the side effect obvious in name and docstring |
| Tool may fail from external systems | Return clear recoverable errors or raise intentionally |
| Tool output is consumed by another deterministic step | Return structured dict/list, not prose |

</tool-selection>

<basic-tool>

```python
from agents import Agent, Runner, function_tool

@function_tool
def lookup_order(order_id: str) -> dict:
    """Look up a customer order by ID."""
    return {"order_id": order_id, "status": "shipped"}

agent = Agent(
    name="orders",
    instructions="Use tools to answer order questions.",
    tools=[lookup_order],
)

result = Runner.run_sync(agent, "What is the status of order A123?")
```

</basic-tool>

<context-tool>

```python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper, function_tool

@dataclass
class RequestContext:
    tenant_id: str

@function_tool
def tenant_name(ctx: RunContextWrapper[RequestContext]) -> str:
    """Return the current tenant identifier."""
    return ctx.context.tenant_id

agent = Agent[RequestContext](
    name="tenant-agent",
    instructions="Use tenant-aware tools when answering.",
    tools=[tenant_name],
)
```

</context-tool>

<tool-design-rules>

- Name tools with verbs: `fetch_document`, `validate_slides`, `render_pptx`.
- Write docstrings as model-facing API contracts. Include when to call the tool and what identifiers mean.
- Prefer concrete scalar parameters and typed containers over free-form JSON strings.
- Return short structured data. Put large payloads in files or object storage and return paths/IDs.
- Make irreversible operations explicit: `send_email`, `delete_record`, `publish_deck`.
- Do not hide auth, tenancy, or user identity in model text. Pass it through context.

</tool-design-rules>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Tool returns a long Markdown document | Save it and return a file path plus summary |
| Tool takes `query: str` for everything | Use typed parameters that match the operation |
| Tool silently mutates global state | Make state explicit in context or persistent storage |
| Tool catches all exceptions and returns vague text | Return actionable failure data or raise a clear error |
| Tool depends on model deciding validation | Put validation in the tool or schema layer |

</common-mistakes>

<workflow-boundary>
In document-to-artifact workflows, use tools for IO and rendering, not for free-form planning. Example boundary: `fetch_doc` and `render_pptx` are tools; deciding slide emphasis is an agent step.
</workflow-boundary>


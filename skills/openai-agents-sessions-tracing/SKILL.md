---
name: openai-agents-sessions-tracing
description: "INVOKE THIS SKILL when adding, reviewing, or debugging sessions, tracing, streaming, run history, trace metadata, or observability in an OpenAI Agents SDK Python app."
---

# OpenAI Agents Sessions And Tracing

<overview>
Use sessions for conversation continuity and tracing for visibility into agent runs. Treat traces as debugging and evaluation artifacts. Do not put secrets or sensitive raw payloads into trace metadata.
</overview>

<when-to-use>

| Need | Use |
| --- | --- |
| Multi-turn conversation state | Session support |
| Reproduce a failed run | Trace ID plus input snapshot |
| Live UI updates | Streaming run events |
| Debug tool calls or handoffs | Tracing |
| Compare behavior across model changes | Stable eval prompts plus traces |

</when-to-use>

<streaming-pattern>

Use streaming when the product needs partial visibility. Keep business decisions based on final validated output, not arbitrary partial deltas.

```python
from agents import Agent, Runner

agent = Agent(name="assistant", instructions="Answer with concise updates.")

async def stream_answer(prompt: str):
    result = Runner.run_streamed(agent, prompt)
    async for event in result.stream_events():
        # Route event types to UI/logging as appropriate for the current SDK version.
        print(event)
```

</streaming-pattern>

<tracing-rules>

- Include stable run metadata: workflow name, tenant/workspace ID, request ID, app version.
- Exclude secrets, raw credentials, and unnecessary full documents.
- Preserve input/output fixtures for bugs that need reproduction.
- Use traces to inspect tool calls, handoffs, guardrail trips, and model behavior.
- Keep trace naming consistent across workflows.

</tracing-rules>

<session-rules>

- Use sessions for conversation history, not for durable business state.
- Store business records in application storage and reference them by ID.
- Make session IDs deterministic enough to recover the right conversation.
- Do not rely on session history to carry required tool parameters forever; revalidate required IDs.

</session-rules>

<testing-debugging-pattern>

Test sessions, tracing, and streaming at observable boundaries. Streaming tests should collect events for UI behavior, but downstream validation should wait for the completed run state.

```python
from uuid import uuid4

from agents import Agent, Runner, SQLiteSession, trace

agent = Agent(name="assistant", instructions="Reply concisely.")

async def run_with_session(message: str, *, session_id: str) -> str:
    session = SQLiteSession(session_id)
    result = await Runner.run(agent, message, session=session)
    return result.final_output

async def stream_with_trace(prompt: str) -> list[str]:
    conversation_id = uuid4().hex[:16]
    chunks: list[str] = []
    with trace("assistant-stream", group_id=conversation_id):
        result = Runner.run_streamed(agent, input=prompt)
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                chunks.append(str(event.data))
    return chunks
```

| Scenario | Check |
| --- | --- |
| Session continuity | Same `SQLiteSession(session_id)` preserves conversation context |
| Streaming UI | Collect streamed events, but validate final artifacts after completion |
| Trace grouping | Use stable request/conversation IDs with `trace(..., group_id=...)` |
| Secret negative test | Assert trace metadata excludes API keys, tokens, and raw private documents |
| Failure reproduction | Preserve request ID, model, prompt version, input reference, and validation errors |

When debugging, inspect trace spans, tool calls, handoffs, guardrail trips, generated items, and failure context before changing prompts. Treat traces as observability artifacts, not durable business records.

</testing-debugging-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Streaming partial text directly into downstream JSON parser | Wait for final structured output |
| Trace metadata includes API keys or full private documents | Redact and store references |
| Session history becomes the only source of business truth | Store business state separately |
| Failed runs cannot be reproduced | Log request ID, model, prompt version, and input references |
| Tool/handoff issues debugged from final text only | Inspect traces and generated items |
| Tests only assert streamed text | Also test final state, session continuity, and failure handling |
| Trace grouping changes every subsystem | Use one stable request or conversation ID across the workflow |

</common-mistakes>

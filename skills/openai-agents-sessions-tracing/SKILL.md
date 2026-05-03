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

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Streaming partial text directly into downstream JSON parser | Wait for final structured output |
| Trace metadata includes API keys or full private documents | Redact and store references |
| Session history becomes the only source of business truth | Store business state separately |
| Failed runs cannot be reproduced | Log request ID, model, prompt version, and input references |
| Tool/handoff issues debugged from final text only | Inspect traces and generated items |

</common-mistakes>


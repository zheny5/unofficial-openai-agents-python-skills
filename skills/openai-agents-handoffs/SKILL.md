---
name: openai-agents-handoffs
description: "INVOKE THIS SKILL when designing or modifying multi-agent routing, handoffs, specialist agents, or agent-as-tool patterns in an OpenAI Agents SDK Python app."
---

# OpenAI Agents Handoffs

<overview>
Use handoffs when control should move to a specialized agent. Do not use handoffs just to call deterministic code; use tools for that. Handoffs work best when each target agent has a clear domain, instructions, and output expectation.
</overview>

<handoff-vs-tool>

| Need | Use |
| --- | --- |
| Fetch data, write file, call API, render artifact | Tool |
| Switch conversation/task ownership to another specialist | Handoff |
| Get a bounded sub-result while current agent remains in control | Agent-as-tool pattern |
| Route among multiple expert policies | Handoff with explicit routing instructions |

</handoff-vs-tool>

<basic-handoff>

```python
from agents import Agent, Runner

billing_agent = Agent(
    name="billing",
    instructions="Handle billing questions. Ask for missing invoice IDs.",
)

support_agent = Agent(
    name="support",
    instructions="Handle general support. Handoff billing issues.",
    handoffs=[billing_agent],
)

result = Runner.run_sync(support_agent, "I need help with invoice INV-123.")
```

</basic-handoff>

<routing-design>

Write routing instructions as explicit ownership rules:

```text
If the user asks about invoices, payments, refunds, or tax receipts, hand off to billing.
If the user asks about account access or product usage, continue handling the request.
Do not hand off just because a billing-related word appears in an unrelated context.
```

</routing-design>

<specialist-agent-rules>

- Give each specialist a narrow name and responsibility.
- Avoid overlapping domains unless the router has a clear tie-breaker.
- Keep shared constraints in a shared factory/helper, not copied manually into every prompt.
- Make final output expectations clear for each specialist.
- Add tests for routing examples and near-misses.

</specialist-agent-rules>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Handoff used to run deterministic code | Use a tool |
| Specialist agents have vague overlapping responsibilities | Define routing ownership and tie-breakers |
| Handoff chain is many levels deep | Flatten routing or use a workflow orchestrator |
| No tests for routing | Add examples for expected handoff and expected no-handoff |
| User state disappears after handoff | Pass required state through context or structured inputs |

</common-mistakes>


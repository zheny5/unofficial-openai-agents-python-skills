---
name: openai-agents-guardrails
description: "INVOKE THIS SKILL when adding or reviewing input guardrails, output guardrails, policy checks, validation gates, or business-rule enforcement in an OpenAI Agents SDK Python app."
---

# OpenAI Agents Guardrails

<overview>
Guardrails are validation gates around agent runs. Use them for safety policy, business constraints, format checks, and early rejection. They complement tools and schemas; they are not a replacement for deterministic validation in downstream code.
</overview>

<guardrail-selection>

| Need | Use |
| --- | --- |
| Reject or classify unsafe/unsupported user input | Input guardrail |
| Validate final answer before returning it | Output guardrail |
| Enforce renderer/API invariants | Deterministic validator, optionally as output guardrail |
| Require human approval | Workflow approval or separate control layer |
| Prevent side effects | Tool design and permission checks |

</guardrail-selection>

<design-rules>

- Guardrails should be cheap, focused, and testable.
- Separate policy classification from user-facing response text.
- Prefer structured guardrail results over prose.
- Treat guardrail failures as product states with clear handling.
- Keep non-negotiable business validation in deterministic code too.

</design-rules>

<example-shape>

```python
from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, Runner, RunContextWrapper, input_guardrail

class SafetyCheck(BaseModel):
    allowed: bool
    reason: str

safety_agent = Agent(
    name="safety-check",
    instructions="Classify whether the request is allowed. Return only the structured result.",
    output_type=SafetyCheck,
)

@input_guardrail
async def safety_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str,
) -> GuardrailFunctionOutput:
    result = await Runner.run(safety_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.allowed,
    )
```

Use this pattern as a focused classifier. Attach it with `input_guardrails=[safety_input_guardrail]`, then test both pass and tripwire paths.

</example-shape>

<output-guardrail-pattern>

Output guardrails receive the typed final output. Use them when the agent can finish normally but the final artifact still needs a policy or quality gate.

```python
from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, output_guardrail

class MessageOutput(BaseModel):
    response: str

@output_guardrail
async def no_empty_response(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: MessageOutput,
) -> GuardrailFunctionOutput:
    is_empty = not output.response.strip()
    return GuardrailFunctionOutput(
        output_info={"reason": "empty response" if is_empty else "ok"},
        tripwire_triggered=is_empty,
    )

agent = Agent(
    name="checked-agent",
    instructions="Return a non-empty response.",
    output_type=MessageOutput,
    input_guardrails=[safety_input_guardrail],
    output_guardrails=[no_empty_response],
)
```

</output-guardrail-pattern>

<output-validation-pattern>

For generated artifacts:

```python
deck = result.final_output
errors = validate_deck(deck)
if errors:
    raise ValueError(f"Invalid deck spec: {errors}")
```

If the same validation should block user-visible output, expose it as an output guardrail or explicit workflow gate.

</output-validation-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Guardrail prompt tries to solve the whole task | Keep it to classification or validation |
| Only model-based validation protects an API call | Add deterministic checks before side effects |
| Guardrail failure becomes a generic exception | Map it to a clear app-level failure response |
| No negative tests | Test both allowed and blocked examples |
| Output schema validation is skipped because a guardrail exists | Keep schema validation |

</common-mistakes>

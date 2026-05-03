---
name: openai-agents-structured-output
description: "INVOKE THIS SKILL when an OpenAI Agents SDK Python app needs JSON, Pydantic outputs, schemas, validators, or machine-readable artifacts such as plans, records, reports, or slide specs."
---

# OpenAI Agents Structured Output

<overview>
Use structured outputs when downstream code consumes the result. Prefer Pydantic models with explicit fields over asking the model to emit JSON in prose. Keep schemas small, semantic, and aligned with actual renderer or API contracts.
</overview>

<when-to-use>

| Output need | Use |
| --- | --- |
| Human answer only | Plain text `final_output` |
| Machine-readable artifact | `output_type` with Pydantic |
| Renderer/API input | Pydantic schema matching renderer/API |
| Complex validation | Pydantic validators plus deterministic post-checks |
| Large artifacts | File output plus structured manifest |

</when-to-use>

<basic-pydantic-output>

```python
from pydantic import BaseModel, Field
from agents import Agent, Runner

class TaskPlan(BaseModel):
    title: str
    steps: list[str] = Field(min_length=1)
    risks: list[str] = []

planner = Agent(
    name="planner",
    instructions="Return a practical task plan.",
    output_type=TaskPlan,
)

result = Runner.run_sync(planner, "Plan a migration to typed tool outputs.")
plan: TaskPlan = result.final_output
```

</basic-pydantic-output>

<schema-design-rules>

- Use domain nouns: `SlideDeck`, `Slide`, `ChartSpec`, `TaskPlan`.
- Keep fields required unless the absence is meaningful.
- Prefer enums/literals for layout/type choices that code switches on.
- Put prose in bounded fields like `speaker_notes`, not arbitrary nested blobs.
- Validate renderer constraints after model generation.
- Keep chain-of-thought out of schemas. Ask for concise rationale only if the app needs it.

</schema-design-rules>

<artifact-pipeline>

For document-to-artifact workflows, use a stable intermediate schema:

```python
from pydantic import BaseModel, Field

class SlideSpec(BaseModel):
    title: str
    bullets: list[str] = Field(max_length=6)
    speaker_notes: str | None = None

class DeckSpec(BaseModel):
    title: str
    slides: list[SlideSpec] = Field(min_length=1)
```

Then render with deterministic Python code:

```python
deck = result.final_output
validate_deck(deck)
render_pptx(deck, output_path="deck.pptx")
```

</artifact-pipeline>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Prompt says "return JSON" but no schema is enforced | Use `output_type` |
| Schema mirrors internal model thoughts | Schema should mirror downstream data needs |
| Optional fields everywhere | Make required fields explicit and fail fast |
| Renderer accepts whatever the model produced | Validate before rendering or API calls |
| Huge document embedded in output | Store large content separately and return references |

</common-mistakes>


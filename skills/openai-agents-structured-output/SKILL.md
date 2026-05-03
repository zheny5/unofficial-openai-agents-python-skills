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

<testing-debugging-pattern>

Test structured output at the typed boundary. The SDK validates model JSON into the declared `output_type`; downstream code should validate business constraints before rendering or API calls.

```python
from pydantic import BaseModel, Field

class SlideSpec(BaseModel):
    title: str
    bullets: list[str] = Field(min_length=1, max_length=6)

class DeckSpec(BaseModel):
    title: str
    slides: list[SlideSpec] = Field(min_length=1)

def validate_deck(deck: DeckSpec) -> list[str]:
    errors: list[str] = []
    for index, slide in enumerate(deck.slides, start=1):
        if len(slide.title) > 80:
            errors.append(f"slide {index}: title too long")
    return errors

def test_validate_deck_rejects_long_title() -> None:
    deck = DeckSpec(title="Demo", slides=[SlideSpec(title="x" * 81, bullets=["point"])])
    assert validate_deck(deck) == ["slide 1: title too long"]
```

| Scenario | Check |
| --- | --- |
| Successful typed output | `isinstance(result.final_output, DeckSpec)` |
| Negative schema test | Invalid fixtures fail Pydantic validation or deterministic validation |
| Renderer boundary | Renderer accepts `DeckSpec`, not raw JSON text |
| Debug/failure case | Preserve prompt version, schema version, and validation errors |

For schemas that are not strict-compatible, confirm the need in source/docs and wrap the type with `AgentOutputSchema(YourType, strict_json_schema=False)`. Do not disable strict schema just to avoid fixing a weak output model.

</testing-debugging-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Prompt says "return JSON" but no schema is enforced | Use `output_type` |
| Schema mirrors internal model thoughts | Schema should mirror downstream data needs |
| Optional fields everywhere | Make required fields explicit and fail fast |
| Renderer accepts whatever the model produced | Validate before rendering or API calls |
| Huge document embedded in output | Store large content separately and return references |
| Tests parse JSON strings from `final_output` | Assert the typed object returned by `output_type` |
| Validation failures are hard to reproduce | Log schema version, input reference, and validation errors |

</common-mistakes>

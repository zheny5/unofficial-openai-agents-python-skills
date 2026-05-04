---
name: openai-agents-implementation-strategy
description: "INVOKE THIS SKILL when planning OpenAI Agents SDK Python changes that may affect compatibility boundaries, persisted state, runtime behavior, or validation sequencing. Use it to decide whether a shim, migration, or direct rewrite is the right move."
---

# OpenAI Agents Implementation Strategy

<overview>
Use this skill before editing runtime code or public examples. First classify the change surface, then pick the smallest safe implementation. Prefer direct rewrites for unreleased interfaces and only add compatibility layers when a released `compatibility boundary` is actually at risk.
</overview>

<surface-classification>

| Surface | Default stance |
| --- | --- |
| Released public API | Preserve compatibility or document migration |
| Persisted schema / serialized state | Treat as compatibility-sensitive |
| CLI / config / env surface | Treat as compatibility-sensitive |
| Branch-local helper or example | Rewrite directly |
| Docs/examples only | Update directly |

</surface-classification>

<workflow>

1. Identify the exact surface: API, state, config, docs, or internal helper.
2. Find the latest release boundary from `origin` before judging breakage.
3. Compare against the latest released contract, not against branch-local churn.
4. Prefer deletion or replacement over alias layers for unreleased shapes.
5. Add a shim only when a released consumer or durable external boundary requires it.

</workflow>

<decision-rules>

- If the change only touches unreleased code on the current branch, rewrite it directly.
- If the change alters `RunState`, session persistence, or documented config, treat it as durable.
- If the task is docs/examples only, keep the implementation narrow and avoid runtime changes.
- If the change needs a migration path, define the migration before editing callers.
- Validate any changed schema or structured state shape with deterministic tests before changing prompts or examples.

</decision-rules>

<testing-debugging-pattern>

For compatibility-sensitive changes, write tests around the boundary rather than only the happy path:

- Positive test: current released behavior still works.
- Negative test: unsupported old shape fails with a clear error or migration path.
- Failure debug context: record release tag, source map entry, affected schema, trace ID, tool surface, and request ID when applicable.
- Deterministic validation: compare structured state or config values directly, not prose.

</testing-debugging-pattern>

<example>

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ChangeSurface:
    name: str
    released: bool
    durable_state: bool
    config_or_env: bool

def needs_migration(surface: ChangeSurface) -> bool:
    return surface.released or surface.durable_state or surface.config_or_env
```

</example>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Treating branch-local churn as a released contract | Recheck against the latest release tag |
| Adding a shim without a released consumer | Rewrite the branch-local shape directly |
| Changing durable state without thinking about migration | Decide the boundary before editing |
| Mixing docs-only work with runtime refactors | Split the change and keep the current task narrow |
| Testing only final text | Validate structured state, schema, and failure behavior |

</common-mistakes>

<notes>
- Use this skill to set the implementation boundary, not to design the whole feature.
- If the task crosses a real release boundary, call that out explicitly in the handoff.
</notes>

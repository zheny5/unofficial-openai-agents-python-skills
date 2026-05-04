---
name: openai-agents-docs-sync
description: "INVOKE THIS SKILL when comparing skill guidance or docs against the official openai-agents-python repository and updating source maps, examples, or docs to match upstream behavior."
---

# OpenAI Agents Docs Sync

<overview>
Use this skill when you need to keep this skills repo aligned with the official openai-agents-python source. First map the feature to the correct upstream file or doc page, then update only the relevant guidance. Do not guess API details when the source checkout can answer them. Preserve structured examples, schema details, and deterministic validation guidance.
</overview>

<source-first>

Before editing any API example, inspect the official source checkout or docs and confirm:

- the symbol or call shape
- the current example path
- the release boundary that matters

</source-first>

<workflow>

1. Inventory the feature or behavior that needs documentation.
2. Find the upstream source file, doc page, or official skill that proves it.
3. Do a doc-first pass: check whether the local skill already claims the behavior.
4. Do a code-first pass: compare the claim against the official source checkout.
5. Build a feature inventory with source path, symbol, config, and test evidence.
6. Compare the existing skill text against the source-backed facts.
7. Update the smallest relevant section.
8. Validate the source map, expected terms, and English docs references if they changed.

</workflow>

<mapping-rules>

- Prefer existing sections over creating new pages.
- Keep examples short and source-backed.
- If the upstream repo moved or renamed a behavior, update the mapping first.
- Leave translated or unrelated docs alone unless the task explicitly needs them.
- Prefer English docs when syncing official documentation coverage.

</mapping-rules>

<inventory-shape>

```python
feature = {
    "name": "session persistence",
    "source": "src/agents/run_internal/session_persistence.py",
    "docs": "docs/sessions/index.md",
    "skill": "openai-agents-sessions-tracing",
    "schema_or_tool": "SessionSettings",
}
```

</inventory-shape>

<testing-debugging-pattern>

After a docs sync, test the guidance itself:

- Run static eval to catch missing source map coverage.
- Use a live eval dry-run to verify task prompts still load.
- Validate changed code blocks with syntax checks where possible.
- Add a negative drift note when upstream and local guidance disagree.
- Preserve debug evidence: upstream commit, source path, trace or issue ID, and failure mode.

</testing-debugging-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Editing from memory instead of the source checkout | Verify the upstream file first |
| Updating text without refreshing the source map | Sync the mapping and fixtures together |
| Spreading one feature across multiple pages | Put the guidance on the most relevant page |
| Treating stale branch-local docs as current upstream | Recheck the latest official commit |
| Updating prose without tests | Run static eval and validate affected examples |
| Letting live prompt examples leak unsafe provider settings | Call out safe defaults such as tracing controls and explicit client config |

</common-mistakes>

<notes>
- Use this skill for maintenance and drift control, not for broad feature design.
- When the source and the skill disagree, the source wins.
</notes>

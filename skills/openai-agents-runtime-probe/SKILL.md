---
name: openai-agents-runtime-probe
description: "INVOKE THIS SKILL when you need to design or run local or live runtime probes for OpenAI Agents SDK Python behavior. Use it for session, streaming, error, retry, and state-repetition investigations that need a case matrix instead of guesswork."
---

# OpenAI Agents Runtime Probe

<overview>
Use this skill to verify runtime behavior, not to restate docs. Start with a small matrix, include at least one control when comparing behavior, and record what actually happened. Do not stop at the happy path if the real question is about drift, failure, negative cases, structured outputs, schema validation, or state sensitivity.
</overview>

<matrix-first>

Build the case matrix before running probes. Keep the matrix small enough to answer the question but large enough to expose the likely failure mode.

| case_id | scenario | mode | question | setup | result_flag | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | baseline success | single-shot | What is the normal behavior? | valid input and fresh state | pending | pending |
| C1 | control | single-shot | Does the baseline still hold? | same probe against control target | pending | pending |
| E1 | error case | single-shot | How does the runtime fail on bad input? | malformed or missing config | pending | pending |
| R1 | repetition | repeat-3 | Does repeated execution change the result? | same request, controlled state | pending | pending |

</matrix-first>

<execution-rules>

- Start with a control or known-good case when the question implies regression or drift.
- Use `single-shot`, `repeat-N`, or `warm-up + repeat-N` intentionally.
- Mark whether state is fresh, reused, or cache-busted.
- If the probe reads env vars or hits live services, name the exact variables first and get approval.
- Prefer runtime evidence over static assumptions when the runtime surface is the question.

</execution-rules>

<capture>

Record the request shape, response shape, errors, timing, repeats, and cleanup behavior. For OpenAI-related probes, also capture request IDs or other stable run identifiers when available. If output is comparative, say whether the result supports only pattern parity or a broader claim.

</capture>

<probe-shape>

```python
MATRIX = [
    {"case_id": "S1", "scenario": "baseline", "mode": "single-shot", "state": "fresh"},
    {"case_id": "R1", "scenario": "repeat session", "mode": "repeat-3", "state": "reused"},
]

def record(case: dict, *, observation: str, result_flag: str, evidence: str) -> dict:
    return {**case, "observation_summary": observation, "result_flag": result_flag, "evidence": evidence}
```

</probe-shape>

<testing-debugging-pattern>

Turn the matrix into executable checks when possible:

- Validate deterministic fields such as event type, final output type, session ID, schema status, and error class.
- Keep UI streaming assertions separate from final structured output assertions.
- Include at least one failure or negative case when the probe is meant to harden production behavior.
- Preserve enough debug context to reproduce the case without logging secrets: trace ID, tool name, model, state setup, and input reference.

</testing-debugging-pattern>

<common-mistakes>

| Mistake | Fix |
| --- | --- |
| Running only the happy path | Add error, repetition, or control cases |
| Using hidden state without documenting it | Record fresh/reused state explicitly |
| Reading secrets without approval | Name the env vars first and wait |
| Treating one run as a durable conclusion | Repeat the case or narrow the claim |
| Mixing several questions in one probe | Split the matrix into separate cases |
| Parsing partial stream text as structured data | Wait for final output, then validate the schema |

</common-mistakes>

<notes>
- Keep probes disposable and focused.
- Keep temporary artifacts until the report is written, then remove them unless needed for follow-up.
</notes>

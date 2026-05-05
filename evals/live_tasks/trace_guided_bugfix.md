# Live Task: Trace Guided Bugfix

Write a compact OpenAI Agents SDK Python debug helper for a session +
streaming bug.

It must include:

- `request_id`
- `trace(..., group_id=...)`
- `Runner.run_streamed(...)`
- `session=`
- one final validated output check
- one failure reproduction checklist
- one secret-redaction note

Return exactly one valid Python code block.
Include the literal words `reproduce`, `secret`, `failure`, and `validate` in comments or string constants.

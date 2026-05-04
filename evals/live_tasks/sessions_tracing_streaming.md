# Live Task: Sessions, Tracing, Streaming

Write a compact OpenAI Agents SDK Python workflow that demonstrates:

- `SQLiteSession` conversation continuity
- `Runner.run_streamed(...).stream_events()`
- `trace(..., group_id=...)`
- what to test for streamed UI events versus final validated output
- how to avoid leaking secrets or raw private documents into trace metadata

Include one failure-reproduction checklist.

Return exactly one valid Python code block. Include the failure-reproduction checklist as Python comments or a string constant inside the code block.
The code must include a literal `request_id` and must distinguish streamed UI events from final validated output.
Include the literal phrase `request ID` in a comment or string constant.
Do not include mock raw private document contents such as `PRIVATE:` snippets; describe redaction abstractly instead.
Use the literal `session=` keyword in `Runner.run(...)` or `Runner.run_streamed(...)`.

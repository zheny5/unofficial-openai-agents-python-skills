# Runtime Eval Report

Generated: `2026-05-04T15:41:00.623745+00:00`
Source checkout: `/home/yuzheng/projects/openai-agents-python`
Source commit: `9b57f057`
Returncode: `0`
Passed: `5/5`

## Cases

- `minimal_runner`: `pass`
  Details: `{"final_output": "hello from fake runtime"}`
- `structured_output`: `pass`
  Details: `{"final_output": {"city": "Tokyo", "temperature_c": 22}}`
- `tool_call`: `pass`
  Details: `{"calls": ["Paris"], "final_output": "Paris is 22C."}`
- `streaming`: `pass`
  Details: `{"event_count": 11, "final_output": "streamed final"}`
- `session`: `pass`
  Details: `{"item_count": 4, "second_input_items": 3}`

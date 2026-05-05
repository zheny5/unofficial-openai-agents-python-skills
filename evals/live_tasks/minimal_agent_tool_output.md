# Live Task: Minimal Agent + Tool + Structured Output

Write a small OpenAI Agents SDK Python module that defines:

- one `Agent`
- one `@function_tool`
- one Pydantic output model via `output_type`
- an async function that calls the agent and returns the typed `final_output`
- one minimal pytest-style test or test scenario

Keep side effects inside tools, not prompts. Do not parse JSON from a string response.

Return exactly one valid Python code block. Do not include preamble text, tool calls, or explanations outside the code block.
The code must include a typed return annotation for the async wrapper and must validate `final_output` in the test with `assert` or `isinstance`.
Include the literal words `typed`, `validate`, and `test` in code comments or test names.

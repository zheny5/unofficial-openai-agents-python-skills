# Live Task: Runtime Behavior Probe

Write a compact Python probe for an OpenAI Agents SDK runtime question.

It should:

- define a small validation matrix
- include a control case
- cover one repeat-sensitive or failure-sensitive case
- show how you would record fresh vs reused state

Return exactly one valid Python code block. The code should define a matrix list and a helper that records case observations. Do not include preamble text, tool calls, or explanations outside the code block.

The Python code must include these literal dictionary keys:

- `case_id`
- `scenario`
- `mode`
- `question`
- `setup`
- `result_flag`
- `evidence`

The matrix must include the literal strings `control`, `repeat-3`, `warm-up`, and `cleanup`.

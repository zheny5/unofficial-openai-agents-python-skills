# AutoResearch Program

Use this loop to improve the OpenAI Agents Python skills without relying on subjective judgment.

1. Run the static evaluator:

   ```bash
   python3 evals/run_static_eval.py --format markdown
   ```

2. Pick exactly one concrete weakness from the report.
3. Form a hypothesis in one sentence, for example:

   ```text
   Adding concrete input/output guardrail examples will improve API correctness for guardrail tasks.
   ```

4. Edit only the relevant `skills/**/SKILL.md` files.
5. Rerun the evaluator.
6. Keep the change only if:
   - total score improves,
   - no hard failures are introduced,
   - the edited skill remains concise and task-focused.
7. Record notable experiments in `evals/results/history.tsv` when committing a successful iteration.

Do not optimize for evaluator terms by stuffing keywords. Add accurate, useful guidance that would help a coding agent write better OpenAI Agents SDK Python code.


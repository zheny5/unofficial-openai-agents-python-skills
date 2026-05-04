# AutoResearch Program

Use this loop to improve the OpenAI Agents Python skills without relying on subjective judgment.

1. Run the static evaluator:

   ```bash
   python3 evals/run_static_eval.py --format markdown
   ```

2. Run the runtime evaluator when changing SDK-runtime guidance:

   ```bash
   python3 evals/run_runtime_eval.py --format markdown
   ```

3. Pick exactly one concrete weakness from the report.
4. Form a hypothesis in one sentence, for example:

   ```text
   Adding concrete input/output guardrail examples will improve API correctness for guardrail tasks.
   ```

5. Edit only the relevant `skills/**/SKILL.md` files.
6. Rerun the relevant evaluators.
7. Keep the change only if:
   - total score improves,
   - no hard failures are introduced,
   - the edited skill remains concise and task-focused.
8. Record notable experiments in `evals/results/history.tsv` when committing a successful iteration.

Before changing SDK API examples, inspect `references/source-map.md` and confirm the symbol or call shape against the official source checkout or docs. Engineering-only guidance can use the current eval report, but new imports, decorators, model wrappers, guardrail signatures, or output schema patterns require source confirmation.

Do not optimize for evaluator terms by stuffing keywords. Add accurate, useful guidance that would help a coding agent write better OpenAI Agents SDK Python code.

The runtime evaluator is the standard for "actually used the library": it must execute `Agent` and `Runner` from the official checkout and assert SDK result objects, not just parse generated code.

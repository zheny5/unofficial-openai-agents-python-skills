#!/usr/bin/env python3
"""Optional live forward-test harness for the OpenAI Agents Python skills."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "evals" / "fixtures" / "live_expected_terms.yaml"
RESULTS_DIR = ROOT / "evals" / "results" / "live"


@dataclass
class LiveTask:
    name: str
    prompt_file: Path
    expected_terms: list[str]
    architecture_terms: list[str]
    banned_patterns: list[str]


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text())


def load_tasks(selected: str | None = None) -> list[LiveTask]:
    config = load_config()
    tasks: list[LiveTask] = []
    for name, raw in config["tasks"].items():
        if selected and name != selected:
            continue
        tasks.append(
            LiveTask(
                name=name,
                prompt_file=ROOT / raw["prompt_file"],
                expected_terms=raw["expected_terms"],
                architecture_terms=raw["architecture_terms"],
                banned_patterns=raw["banned_patterns"],
            )
        )
    if selected and not tasks:
        raise SystemExit(f"unknown task: {selected}")
    return tasks


def build_prompt(task: LiveTask) -> str:
    task_text = task.prompt_file.read_text()
    return f"""You are evaluating whether local Agent Skills help write OpenAI Agents SDK Python code.

Use the installed/local skills conceptually if they are available, especially the OpenAI Agents Python skills.
Do not edit files. Do not run tools. Output only the code or implementation guidance requested by the task.

Task:
{task_text}
"""


def claude_command(prompt: str) -> list[str]:
    return [
        "claude",
        "-p",
        prompt,
        "--permission-mode",
        "default",
        "--tools",
        "",
        "--no-session-persistence",
        "--output-format",
        "json",
    ]


def output_text(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    for key in ("result", "content", "text", "message"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return raw


def contains(text: str, pattern: str) -> bool:
    return pattern.lower() in text.lower()


def score_output(task: LiveTask, text: str) -> dict[str, Any]:
    missing_expected = [term for term in task.expected_terms if not contains(text, term)]
    missing_architecture = [term for term in task.architecture_terms if not contains(text, term)]
    banned_found = [pattern for pattern in task.banned_patterns if contains(text, pattern)]
    expected_score = (len(task.expected_terms) - len(missing_expected)) / len(task.expected_terms)
    architecture_score = (
        (len(task.architecture_terms) - len(missing_architecture)) / len(task.architecture_terms)
        if task.architecture_terms
        else 1.0
    )
    banned_penalty = min(len(banned_found) * 0.25, 1.0)
    total = max((expected_score * 0.6) + (architecture_score * 0.4) - banned_penalty, 0.0)
    return {
        "score": round(total, 3),
        "expected_score": round(expected_score, 3),
        "architecture_score": round(architecture_score, 3),
        "missing_expected_terms": missing_expected,
        "missing_architecture_terms": missing_architecture,
        "banned_patterns_found": banned_found,
    }


def run_task(task: LiveTask, dry_run: bool) -> dict[str, Any]:
    prompt = build_prompt(task)
    cmd = claude_command(prompt)
    if dry_run:
        return {
            "task": task.name,
            "dry_run": True,
            "command": cmd[:1] + ["-p", "<prompt>", *cmd[3:]],
            "prompt_chars": len(prompt),
        }

    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        timeout=180,
    )
    text = output_text(completed.stdout)
    result = {
        "task": task.name,
        "dry_run": False,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
        "output": text,
        "score": score_output(task, text),
    }
    return result


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Live Eval Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Agent: `{report['agent']}`",
        f"Dry run: `{report['dry_run']}`",
        "",
        "## Tasks",
        "",
    ]
    for result in report["results"]:
        if result.get("dry_run"):
            lines.append(
                f"- `{result['task']}`: dry run, prompt chars `{result['prompt_chars']}`"
            )
            continue
        score = result["score"]
        lines.append(
            f"- `{result['task']}`: score `{score['score']}`, returncode `{result['returncode']}`"
        )
        if score["missing_expected_terms"]:
            lines.append(f"  Missing expected: {', '.join(score['missing_expected_terms'])}")
        if score["missing_architecture_terms"]:
            lines.append(
                f"  Missing architecture: {', '.join(score['missing_architecture_terms'])}"
            )
        if score["banned_patterns_found"]:
            lines.append(f"  Banned patterns: {', '.join(score['banned_patterns_found'])}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["claude"], default="claude")
    parser.add_argument("--task")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--write-results", action="store_true")
    args = parser.parse_args()

    results = [run_task(task, args.dry_run) for task in load_tasks(args.task)]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agent": args.agent,
        "dry_run": args.dry_run,
        "results": results,
    }

    output = (
        json.dumps(report, indent=2, sort_keys=True)
        if args.format == "json"
        else render_markdown(report)
    )
    print(output)

    if args.write_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        stem = "dry_run" if args.dry_run else "latest"
        (RESULTS_DIR / f"{stem}.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        (RESULTS_DIR / f"{stem}.md").write_text(render_markdown(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

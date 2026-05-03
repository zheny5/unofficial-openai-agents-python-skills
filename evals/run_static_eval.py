#!/usr/bin/env python3
"""Static evaluator for OpenAI Agents Python coding skills.

The files named *.yaml in this repo are JSON-compatible YAML so the evaluator
can stay dependency-free.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
RUBRIC_PATH = ROOT / "evals" / "rubric.yaml"
TERMS_PATH = ROOT / "evals" / "fixtures" / "expected_terms.yaml"
SOURCE_TERMS_PATH = ROOT / "evals" / "fixtures" / "source_terms.yaml"
RESULTS_DIR = ROOT / "evals" / "results"


@dataclass
class Skill:
    name: str
    path: Path
    frontmatter: dict[str, str]
    body: str
    text: str


def load_json_yaml(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError("malformed frontmatter")
    _, raw_frontmatter, body = parts
    frontmatter: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter, body


def discover_skills() -> tuple[dict[str, Skill], list[str]]:
    skills: dict[str, Skill] = {}
    failures: list[str] = []
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        try:
            frontmatter, body = parse_frontmatter(path)
        except ValueError as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        name = frontmatter.get("name", "")
        if not name:
            failures.append(f"{path.relative_to(ROOT)}: missing name")
            continue
        if name != path.parent.name:
            failures.append(
                f"{path.relative_to(ROOT)}: name {name!r} does not match directory {path.parent.name!r}"
            )
        if name in skills:
            failures.append(f"{path.relative_to(ROOT)}: duplicate skill name {name!r}")
        skills[name] = Skill(
            name=name,
            path=path,
            frontmatter=frontmatter,
            body=body,
            text=path.read_text(),
        )
    return skills, failures


def term_present(text: str, term: str) -> bool:
    if re.search(r"\W", term):
        return term.lower() in text.lower()
    return re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE) is not None


def coverage(text: str, terms: list[str]) -> tuple[float, list[str]]:
    if not terms:
        return 1.0, []
    missing = [term for term in terms if not term_present(text, term)]
    return (len(terms) - len(missing)) / len(terms), missing


def fenced_python_count(text: str) -> int:
    return len(re.findall(r"```python\n", text))


def score_eval() -> tuple[dict[str, Any], int]:
    rubric = load_json_yaml(RUBRIC_PATH)
    expected = load_json_yaml(TERMS_PATH)
    skills, hard_failures = discover_skills()

    hard_patterns = rubric["hard_failure_patterns"]
    for skill in skills.values():
        for pattern in hard_patterns:
            if pattern.lower() in skill.text.lower():
                hard_failures.append(f"{skill.path.relative_to(ROOT)}: hard failure pattern {pattern!r}")

    task_results: dict[str, Any] = {}
    api_scores: list[float] = []
    architecture_scores: list[float] = []
    tool_schema_scores: list[float] = []
    testability_scores: list[float] = []

    for task_name, task in expected["tasks"].items():
        task_skills = [skills[name] for name in task["skills"] if name in skills]
        combined = "\n".join(skill.text for skill in task_skills)
        expected_terms = task["expected_terms"]
        architecture_terms = task["architecture_terms"]

        api_score, missing_api = coverage(combined, expected_terms)
        architecture_score, missing_architecture = coverage(combined, architecture_terms)

        boundary_terms = ["tool", "schema", "structured", "deterministic", "validate"]
        boundary_score, missing_boundary = coverage(combined, boundary_terms)

        test_terms = ["test", "tests", "validate", "debug", "trace", "failure", "negative"]
        test_score, missing_test = coverage(combined, test_terms)

        python_examples = fenced_python_count(combined)
        if python_examples == 0:
            api_score *= 0.75

        api_scores.append(api_score)
        architecture_scores.append(architecture_score)
        tool_schema_scores.append(boundary_score)
        testability_scores.append(test_score)

        task_results[task_name] = {
            "skills": task["skills"],
            "api_score": round(api_score, 3),
            "architecture_score": round(architecture_score, 3),
            "tool_schema_score": round(boundary_score, 3),
            "testability_score": round(test_score, 3),
            "missing_api_terms": missing_api,
            "missing_architecture_terms": missing_architecture,
            "missing_boundary_terms": missing_boundary,
            "missing_testability_terms": missing_test,
            "python_examples": python_examples,
        }

    trigger_scores: list[float] = []
    for skill in skills.values():
        desc = skill.frontmatter.get("description", "")
        lines = len(skill.text.splitlines())
        score = 1.0
        if "INVOKE THIS SKILL" not in desc:
            score -= 0.4
        if lines > rubric["max_skill_lines"]:
            score -= 0.25
        if lines < rubric["min_skill_lines"]:
            score -= 0.25
        if "<common-mistakes>" not in skill.text:
            score -= 0.15
        trigger_scores.append(max(score, 0.0))

    def avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    category_scores = {
        "api_correctness": avg(api_scores),
        "architecture_guidance": avg(architecture_scores),
        "tool_schema_boundary": avg(tool_schema_scores),
        "testability_debuggability": avg(testability_scores),
        "conciseness_trigger_quality": avg(trigger_scores),
    }
    total = sum(category_scores[key] * rubric["weights"][key] for key in category_scores)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_score": round(total, 3),
        "category_scores": {key: round(value, 3) for key, value in category_scores.items()},
        "hard_failures": hard_failures,
        "source_coverage": source_coverage(skills),
        "skills": sorted(skills.keys()),
        "tasks": task_results,
    }
    exit_code = 1 if hard_failures else 0
    return report, exit_code


def source_coverage(skills: dict[str, Skill]) -> dict[str, Any]:
    if not SOURCE_TERMS_PATH.exists():
        return {"enabled": False, "warnings": ["missing evals/fixtures/source_terms.yaml"]}

    config = load_json_yaml(SOURCE_TERMS_PATH)
    source_map_path = ROOT / config["source_map"]
    checkout = Path(config["source_checkout"])
    warnings: list[str] = []
    mapped_skills: dict[str, Any] = {}

    if not source_map_path.exists():
        warnings.append(f"missing {source_map_path.relative_to(ROOT)}")
    if not checkout.exists():
        warnings.append(f"missing source checkout {checkout}")

    source_map_text = source_map_path.read_text() if source_map_path.exists() else ""
    for skill_name, paths in config["skills"].items():
        missing_paths = [path for path in paths if not (checkout / path).exists()]
        if skill_name not in skills:
            warnings.append(f"source map references unknown skill {skill_name}")
        if skill_name not in source_map_text:
            warnings.append(f"{skill_name} missing from source map")
        mapped_skills[skill_name] = {
            "mapped": skill_name in skills and skill_name in source_map_text,
            "missing_paths": missing_paths,
        }

    unmapped = sorted(set(skills) - set(config["skills"]))
    if unmapped:
        warnings.append(f"skills missing source entries: {', '.join(unmapped)}")

    return {
        "enabled": True,
        "source_checkout_exists": checkout.exists(),
        "source_map_exists": source_map_path.exists(),
        "warnings": warnings,
        "skills": mapped_skills,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Static Eval Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Total score: `{report['total_score']}`",
        "",
        "## Category Scores",
        "",
    ]
    for key, value in report["category_scores"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Hard Failures", ""])
    if report["hard_failures"]:
        lines.extend(f"- {failure}" for failure in report["hard_failures"])
    else:
        lines.append("- None")
    source = report.get("source_coverage", {})
    lines.extend(["", "## Source Coverage", ""])
    if not source.get("enabled"):
        lines.append("- Disabled")
    else:
        lines.append(f"- Source checkout exists: `{source['source_checkout_exists']}`")
        lines.append(f"- Source map exists: `{source['source_map_exists']}`")
        warnings = source.get("warnings", [])
        if warnings:
            lines.extend(f"- Warning: {warning}" for warning in warnings)
        else:
            lines.append("- Warnings: none")
    lines.extend(["", "## Task Findings", ""])
    for task_name, result in report["tasks"].items():
        missing = result["missing_api_terms"] + result["missing_architecture_terms"]
        lines.append(
            f"- `{task_name}`: api `{result['api_score']}`, architecture `{result['architecture_score']}`, "
            f"boundary `{result['tool_schema_score']}`, testability `{result['testability_score']}`"
        )
        if missing:
            lines.append(f"  Missing key terms: {', '.join(missing)}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--write-results", action="store_true")
    args = parser.parse_args()

    report, exit_code = score_eval()
    output = json.dumps(report, indent=2, sort_keys=True) if args.format == "json" else render_markdown(report)
    print(output)

    if args.write_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "latest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        (RESULTS_DIR / "latest.md").write_text(render_markdown(report))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

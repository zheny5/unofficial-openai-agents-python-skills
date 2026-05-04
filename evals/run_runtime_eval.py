#!/usr/bin/env python3
"""Runtime evaluator for the OpenAI Agents Python skills.

This is intentionally different from the static and live forward-test evals:
it executes the official SDK runtime with the official repo's FakeModel, so it
can prove Agent/Runner behavior without a real API key.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_TERMS_PATH = ROOT / "evals" / "fixtures" / "source_terms.yaml"
RESULTS_DIR = ROOT / "evals" / "results" / "runtime"


PROBE_CODE = r'''
from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from agents import Agent, Runner, SQLiteSession, function_tool, set_tracing_disabled
from tests.fake_model import FakeModel
from tests.test_responses import (
    get_final_output_message,
    get_function_tool_call,
    get_text_message,
)


set_tracing_disabled(True)


def ok(name: str, **details: Any) -> dict[str, Any]:
    return {"case": name, "passed": True, "details": details}


def fail(name: str, exc: BaseException) -> dict[str, Any]:
    return {"case": name, "passed": False, "error": f"{type(exc).__name__}: {exc}"}


async def minimal_runner() -> dict[str, Any]:
    model = FakeModel()
    model.set_next_output([get_text_message("hello from fake runtime")])
    agent = Agent(name="minimal", model=model)

    result = await Runner.run(agent, "Say hello.")

    assert result.final_output == "hello from fake runtime"
    assert model.last_turn_args["input"] == [{"content": "Say hello.", "role": "user"}]
    return ok("minimal_runner", final_output=result.final_output)


class WeatherReport(BaseModel):
    city: str
    temperature_c: int


async def structured_output() -> dict[str, Any]:
    model = FakeModel()
    model.set_next_output(
        [
            get_final_output_message(
                json.dumps({"city": "Tokyo", "temperature_c": 22})
            )
        ]
    )
    agent = Agent(name="weather", model=model, output_type=WeatherReport)

    result = await Runner.run(agent, "Weather for Tokyo.")

    assert isinstance(result.final_output, WeatherReport)
    assert result.final_output.city == "Tokyo"
    assert result.final_output.temperature_c == 22
    return ok("structured_output", final_output=result.final_output.model_dump())


async def tool_call() -> dict[str, Any]:
    calls: list[str] = []

    @function_tool
    def lookup_city(city: str) -> str:
        """Look up a city in the deterministic test fixture."""
        calls.append(city)
        return f"{city}: 22C"

    model = FakeModel()
    model.add_multiple_turn_outputs(
        [
            [get_function_tool_call("lookup_city", json.dumps({"city": "Paris"}))],
            [get_text_message("Paris is 22C.")],
        ]
    )
    agent = Agent(name="tool-agent", model=model, tools=[lookup_city])

    result = await Runner.run(agent, "Check Paris.")

    assert calls == ["Paris"]
    assert result.final_output == "Paris is 22C."
    assert len(result.raw_responses) == 2
    return ok("tool_call", calls=calls, final_output=result.final_output)


async def streaming() -> dict[str, Any]:
    model = FakeModel()
    model.set_next_output([get_text_message("streamed final")])
    agent = Agent(name="streamer", model=model)

    result = Runner.run_streamed(agent, "Stream once.")
    events = []
    async for event in result.stream_events():
        events.append(event.type)

    assert result.final_output == "streamed final"
    assert events
    return ok("streaming", final_output=result.final_output, event_count=len(events))


async def session_memory() -> dict[str, Any]:
    model = FakeModel()
    model.add_multiple_turn_outputs(
        [
            [get_text_message("San Francisco")],
            [get_text_message("California")],
        ]
    )
    agent = Agent(name="session-agent", model=model)

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "sessions.db"
        session = SQLiteSession("runtime-eval-session", str(db_path))

        first = await Runner.run(agent, "What city is the Golden Gate Bridge in?", session=session)
        second = await Runner.run(agent, "What state is it in?", session=session)
        items = await session.get_items()

    assert first.final_output == "San Francisco"
    assert second.final_output == "California"
    assert len(items) >= 4
    last_input = model.last_turn_args["input"]
    assert isinstance(last_input, list)
    assert len(last_input) > 1
    return ok("session", item_count=len(items), second_input_items=len(last_input))


async def main() -> None:
    cases = [
        minimal_runner,
        structured_output,
        tool_call,
        streaming,
        session_memory,
    ]
    results = []
    for case in cases:
        try:
            results.append(await case())
        except BaseException as exc:
            results.append(fail(case.__name__, exc))
    print(json.dumps({"results": results}, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
'''


def load_source_checkout() -> Path:
    config = json.loads(SOURCE_TERMS_PATH.read_text())
    return Path(config["source_checkout"])


def run_probe(source_checkout: Path, timeout_seconds: int) -> dict[str, Any]:
    if not source_checkout.exists():
        return {
            "returncode": None,
            "stderr": f"missing source checkout: {source_checkout}",
            "stdout": "",
            "results": [],
        }

    with tempfile.NamedTemporaryFile("w", suffix="_runtime_eval.py", delete=False) as handle:
        probe_path = Path(handle.name)
        handle.write(textwrap.dedent(PROBE_CODE).strip() + "\n")

    try:
        env = os.environ.copy()
        pythonpath_parts = [
            str(source_checkout),
            str(source_checkout / "src"),
        ]
        existing_pythonpath = env.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath_parts.append(existing_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
        env.setdefault("OPENAI_API_KEY", "test_key")

        completed = subprocess.run(
            ["uv", "run", "--no-dev", "python", str(probe_path)],
            cwd=source_checkout,
            check=False,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": None,
            "stderr": f"timed out after {timeout_seconds} seconds",
            "stdout": exc.stdout or "",
            "results": [],
        }
    finally:
        probe_path.unlink(missing_ok=True)

    stdout = completed.stdout.strip()
    results: list[dict[str, Any]] = []
    if stdout:
        last_line = stdout.splitlines()[-1]
        try:
            payload = json.loads(last_line)
            results = payload.get("results", [])
        except json.JSONDecodeError:
            results = []

    return {
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
        "stdout": stdout,
        "results": results,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Runtime Eval Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Source checkout: `{report['source_checkout']}`",
        f"Source commit: `{report['source_commit']}`",
        f"Returncode: `{report['returncode']}`",
        f"Passed: `{report['passed']}/{report['total']}`",
        "",
        "## Cases",
        "",
    ]
    for result in report["results"]:
        status = "pass" if result.get("passed") else "fail"
        lines.append(f"- `{result['case']}`: `{status}`")
        if result.get("details"):
            lines.append(f"  Details: `{json.dumps(result['details'], sort_keys=True)}`")
        if result.get("error"):
            lines.append(f"  Error: `{result['error']}`")
    if report.get("stderr"):
        lines.extend(["", "## Stderr", "", "```text", report["stderr"], "```"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--write-results", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    source_checkout = load_source_checkout()
    probe = run_probe(source_checkout, args.timeout_seconds)
    source_commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=source_checkout,
        check=False,
        text=True,
        capture_output=True,
    ).stdout.strip()

    results = probe["results"]
    passed = sum(1 for result in results if result.get("passed"))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_checkout": str(source_checkout),
        "source_commit": source_commit,
        "returncode": probe["returncode"],
        "stderr": probe["stderr"],
        "stdout": probe["stdout"],
        "results": results,
        "passed": passed,
        "total": len(results),
    }

    output = (
        json.dumps(report, indent=2, sort_keys=True)
        if args.format == "json"
        else render_markdown(report)
    )
    print(output)

    if args.write_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / "latest.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        (RESULTS_DIR / "latest.md").write_text(render_markdown(report))

    if probe["returncode"] != 0:
        return 1
    return 0 if passed == len(results) and results else 1


if __name__ == "__main__":
    raise SystemExit(main())

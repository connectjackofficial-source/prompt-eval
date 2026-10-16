"""prompt-eval: tiny framework for evaluating prompts against test cases.

You define test cases with inputs, expected behaviors, and a checker.
The framework runs your prompt function against each case and reports pass/fail.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Case:
    name: str
    prompt: str
    check: Callable[[str], bool]
    description: str = ""


def contains(substring: str) -> Callable[[str], bool]:
    """Pass if output contains the substring."""
    def _check(out: str) -> bool:
        return substring.lower() in out.lower()
    return _check


def matches(pattern: str) -> Callable[[str], bool]:
    """Pass if output matches the regex."""
    rx = re.compile(pattern, re.IGNORECASE)
    return lambda out: bool(rx.search(out))


def not_contains(substring: str) -> Callable[[str], bool]:
    def _check(out: str) -> bool:
        return substring.lower() not in out.lower()
    return _check


def length_between(min_chars: int, max_chars: int) -> Callable[[str], bool]:
    def _check(out: str) -> bool:
        return min_chars <= len(out) <= max_chars
    return _check


def starts_with(prefix: str) -> Callable[[str], bool]:
    """Pass if output starts with the prefix (case-insensitive)."""
    p = prefix.lower()
    return lambda out: out.lower().startswith(p)


def ends_with(suffix: str) -> Callable[[str], bool]:
    """Pass if output ends with the suffix (case-insensitive)."""
    s = suffix.lower()
    return lambda out: out.lower().endswith(s)


@dataclass
class CaseResult:
    name: str
    passed: bool
    output: str
    latency_ms: float


@dataclass
class Report:
    passed: int = 0
    failed: int = 0
    failures: list = field(default_factory=list)
    timings: list = field(default_factory=list)

    @property
    def score(self) -> float:
        total = self.passed + self.failed
        return round(self.passed / total, 3) if total else 1.0

    @property
    def avg_latency_ms(self) -> float:
        if not self.timings:
            return 0.0
        return round(sum(self.timings) / len(self.timings), 2)

    def render(self) -> str:
        lines = [f"prompt-eval: {self.passed} passed, {self.failed} failed "
                 f"(score {self.score}, avg {self.avg_latency_ms}ms/case)"]
        for name, out in self.failures:
            lines.append(f"  FAIL {name}: output={out[:120]!r}")
        return "\n".join(lines)

    def to_json(self) -> str:
        """Machine-readable report for CI or dashboards."""
        import json
        payload = {
            "passed": self.passed,
            "failed": self.failed,
            "score": self.score,
            "avg_latency_ms": self.avg_latency_ms,
            "failures": [{"case": name, "output": out[:200]}
                         for name, out in self.failures],
        }
        return json.dumps(payload, indent=2)


def run(prompt_fn: Callable[[str], str], cases: list[Case]) -> Report:
    """Run prompt_fn(prompt) for each case and check output."""
    import time
    report = Report()
    for case in cases:
        t0 = time.perf_counter()
        output = prompt_fn(case.prompt)
        elapsed = (time.perf_counter() - t0) * 1000
        report.timings.append(round(elapsed, 2))
        if case.check(output):
            report.passed += 1
        else:
            report.failed += 1
            report.failures.append((case.name, output))
    return report


def rank_cases(prompt_fn: Callable[[str], str], cases: list[Case]) -> list:
    """Run every case and rank the results: failures first, then latency.

    Returns [{"name", "passed", "output", "latency_ms"}] so the weakest
    prompt behaviors surface at the top of the list for a quick scan.
    """
    import time
    results = []
    for case in cases:
        t0 = time.perf_counter()
        output = prompt_fn(case.prompt)
        elapsed = (time.perf_counter() - t0) * 1000
        results.append({"name": case.name,
                        "passed": bool(case.check(output)),
                        "output": output[:120],
                        "latency_ms": round(elapsed, 2)})
    results.sort(key=lambda r: (r["passed"], r["latency_ms"]))
    return results


def compare_prompts(prompt_a: Callable[[str], str],
                    prompt_b: Callable[[str], str],
                    cases: list[Case]) -> dict:
    """Head-to-head between two prompt strategies on the same cases.

    Runs both prompt functions over the same case list and returns
    {"a": {...}, "b": {...}, "winner": "a"|"b"} where each side carries
    passed/failed/score/avg latency and wall-clock time. Winning order:
    score first, then latency (faster wins ties).
    """
    import time

    def _run(pfn):
        t0 = time.perf_counter()
        r = run(pfn, cases)
        return {"passed": r.passed, "failed": r.failed,
                "score": r.score,
                "avg_latency_ms": r.avg_latency_ms,
                "wall_ms": round((time.perf_counter() - t0) * 1000, 1)}

    a, b = _run(prompt_a), _run(prompt_b)
    key = lambda x: (x["score"], -x["avg_latency_ms"])
    winner = "a" if key(a) > key(b) else "b"
    return {"a": a, "b": b, "winner": winner}


def report_stats(report: Report, percentiles=(50, 95, 99)) -> dict:
    """Aggregate a report into summary statistics.

    Returns {"passed", "failed", "score", "avg_latency_ms",
    "p50_ms", "p95_ms", "p99_ms", "max_latency_ms"} — the numbers you
    want on a CI badge or in a regression diff.
    """
    timings = sorted(report.timings)
    n = len(timings)

    def pct(p):
        if n == 0:
            return 0.0
        idx = max(0, min(n - 1, int((p / 100.0) * n)))
        return round(timings[idx], 2)

    return {
        "passed": report.passed,
        "failed": report.failed,
        "score": report.score,
        "avg_latency_ms": report.avg_latency_ms,
        "p50_ms": pct(percentiles[0] if percentiles else 50),
        "p95_ms": pct(percentiles[1] if len(percentiles) > 1 else 95),
        "p99_ms": pct(percentiles[2] if len(percentiles) > 2 else 99),
        "max_latency_ms": round(max(timings), 2) if timings else 0.0,
    }


def run_and_save(prompt_fn: Callable[[str], str], cases: list[Case],
                 path: str) -> Report:
    """Run the eval and write the JSON report to *path*."""
    from pathlib import Path
    report = run(prompt_fn, cases)
    Path(path).write_text(report.to_json(), encoding="utf-8")
    return report


# name -> builder(arguments-list) -> checker callable
CHECKER_BUILDERS = {
    "contains": lambda a: contains(a[0]),
    "not_contains": lambda a: not_contains(a[0]),
    "matches": lambda a: matches(a[0]),
    "starts_with": lambda a: starts_with(a[0]),
    "ends_with": lambda a: ends_with(a[0]),
    "length_between": lambda a: length_between(a[0], a[1]),
}


def cases_from_dict(spec: list) -> list:
    """Build Case objects from a plain dict/JSON spec.

    Each item: {"name", "prompt", "check", "check_args", "description"?}
    """
    cases = []
    for item in spec:
        name = item["name"]
        prompt = item["prompt"]
        checker = item["check"]
        args = item.get("check_args", [])
        if checker not in CHECKER_BUILDERS:
            raise ValueError(
                f"unknown checker '{checker}' for case '{name}'; "
                f"use one of: {', '.join(sorted(CHECKER_BUILDERS))}")
        check_fn = CHECKER_BUILDERS[checker](args)
        cases.append(Case(name=name, prompt=prompt, check=check_fn,
                          description=item.get("description", "")))
    return cases

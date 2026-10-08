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

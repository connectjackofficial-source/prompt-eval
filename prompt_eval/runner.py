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


@dataclass
class Report:
    passed: int = 0
    failed: int = 0
    failures: list = field(default_factory=list)

    def render(self) -> str:
        lines = [f"prompt-eval: {self.passed} passed, {self.failed} failed"]
        for name, out in self.failures:
            lines.append(f"  FAIL {name}: output={out[:120]!r}")
        return "\n".join(lines)


def run(prompt_fn: Callable[[str], str], cases: list[Case]) -> Report:
    """Run prompt_fn(prompt) for each case and check output."""
    report = Report()
    for case in cases:
        output = prompt_fn(case.prompt)
        if case.check(output):
            report.passed += 1
        else:
            report.failed += 1
            report.failures.append((case.name, output))
    return report

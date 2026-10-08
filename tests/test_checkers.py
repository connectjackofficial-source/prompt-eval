"""Tests for starts_with, ends_with, and per-case latency."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import (Case, Report, ends_with, run, starts_with)


def test_starts_with():
    check = starts_with("Yes,")
    assert check("Yes, absolutely")
    assert not check("no")
    print("test_starts_with: ok")


def test_ends_with():
    check = ends_with("thank you")
    assert check("ok, thank you")
    assert not check("thanks!")
    print("test_ends_with: ok")


def test_latency_tracked():
    def slow(prompt):
        time.sleep(0.01)
        return "ok"
    cases = [Case(name="c1", prompt="p1", check=starts_with("ok"))]
    report = run(slow, cases)
    assert report.passed == 1
    assert len(report.timings) == 1
    assert report.timings[0] >= 9
    assert report.avg_latency_ms >= 9
    print("test_latency_tracked: ok")


if __name__ == "__main__":
    test_starts_with()
    test_ends_with()
    test_latency_tracked()
    print("prompt-eval checker tests passed")

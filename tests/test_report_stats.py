"""Tests for prompt-eval report_stats."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import Case, Report, report_stats


def test_stats_full():
    r = Report(passed=8, failed=2)
    r.timings = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    s = report_stats(r)
    assert s["passed"] == 8
    assert s["failed"] == 2
    assert s["score"] == 0.8
    assert s["avg_latency_ms"] == 55.0
    assert s["max_latency_ms"] == 100.0
    assert s["p50_ms"] <= s["p95_ms"] <= s["p99_ms"]
    print("test_stats_full: ok")


def test_stats_empty():
    s = report_stats(Report())
    assert s["passed"] == 0 and s["failed"] == 0
    assert s["score"] == 1.0  # vacuous pass
    assert s["max_latency_ms"] == 0.0
    print("test_stats_empty: ok")


def test_stats_single():
    r = Report(passed=1, failed=0)
    r.timings = [42]
    s = report_stats(r)
    assert s["avg_latency_ms"] == 42.0
    assert s["p50_ms"] == 42.0
    print("test_stats_single: ok")


if __name__ == "__main__":
    test_stats_full()
    test_stats_empty()
    test_stats_single()
    print("prompt-eval report_stats tests passed")

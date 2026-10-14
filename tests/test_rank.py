"""Tests for prompt-eval rank_cases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import Case, contains, rank_cases


def _cases():
    return [
        Case("good", "say hi", contains("hi")),
        Case("bad", "say bye", contains("hi")),   # will fail
        Case("slow-bad", "say hello", contains("hi")),  # will fail too
    ]


def _prompt_fn(prompt):
    # deterministic: "bye"/"hello" fail the contains("hi") check
    return {"say hi": "hi there", "say bye": "bye now",
            "say hello": "hello world"}[prompt]


def test_failures_first():
    ranked = rank_cases(_prompt_fn, _cases())
    assert [r["name"] for r in ranked[:2]] == ["bad", "slow-bad"]
    assert ranked[-1]["name"] == "good"
    assert ranked[-1]["passed"] is True
    print("test_failures_first: ok")


def test_latency_sort_within_status():
    ranked = rank_cases(_prompt_fn, _cases())
    failed = [r for r in ranked if not r["passed"]]
    assert failed == sorted(failed, key=lambda r: r["latency_ms"])
    print("test_latency_sort_within_status: ok")


def test_fields():
    ranked = rank_cases(_prompt_fn, _cases())
    assert set(ranked[0]) == {"name", "passed", "output", "latency_ms"}
    assert isinstance(ranked[0]["latency_ms"], float)
    print("test_fields: ok")


if __name__ == "__main__":
    test_failures_first()
    test_latency_sort_within_status()
    test_fields()
    print("prompt-eval rank tests passed")

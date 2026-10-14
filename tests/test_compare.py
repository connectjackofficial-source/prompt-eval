"""Tests for prompt-eval compare_prompts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import Case, compare_prompts, contains


def _cases():
    return [
        Case("greet", "hi", contains("hi")),
        Case("farewell", "bye", contains("bye")),
    ]


def test_winner_by_score():
    a = lambda p: {"hi": "hi there", "bye": "later"}[p]      # fails bye
    b = lambda p: {"hi": "hi", "bye": "bye"}[p]              # both pass
    res = compare_prompts(a, b, _cases())
    assert res["winner"] == "b"
    assert res["a"]["score"] == 0.5
    assert res["b"]["score"] == 1.0
    print("test_winner_by_score: ok")


def test_tie_broken_by_latency():
    fast = lambda p: p * 2
    slow = lambda p: (p * 2, __import__("time").sleep(0.02))[0]
    res = compare_prompts(fast, slow, _cases())
    assert res["winner"] == "a"
    assert res["a"]["avg_latency_ms"] <= res["b"]["avg_latency_ms"]
    print("test_tie_broken_by_latency: ok")


def test_fields():
    res = compare_prompts(lambda p: p, lambda p: p, _cases())
    assert set(res["a"]) == {"passed", "failed", "score",
                             "avg_latency_ms", "wall_ms"}
    assert res["winner"] in ("a", "b")
    print("test_fields: ok")


if __name__ == "__main__":
    test_winner_by_score()
    test_tie_broken_by_latency()
    test_fields()
    print("prompt-eval compare tests passed")

"""Tests for prompt-eval batch 2: stability_check and split_cases."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import Case, contains, stability_check, split_cases


def _flaky_fn(call_count):
    def fn(prompt: str) -> str:
        call_count[0] += 1
        return "yes" if call_count[0] % 2 == 1 else "no"
    return fn


def test_stability_detects_flaky():
    cases = [Case("c1", "q", contains("yes"))]
    cc = [0]
    out = stability_check(_flaky_fn(cc), cases, runs=4)
    assert out[0]["passes"] == 2
    assert out[0]["rate"] == 0.5
    assert out[0]["flaky"] is True
    print("test_stability_detects_flaky: ok")


def test_stability_stable_pass():
    cases = [Case("c1", "q", contains("ok"))]
    out = stability_check(lambda p: "ok always", cases, runs=3)
    assert out[0]["passes"] == 3
    assert out[0]["flaky"] is False
    print("test_stability_stable_pass: ok")


def test_split_cases_deterministic():
    cases = [Case(f"c{i}", f"q{i}", contains("x")) for i in range(10)]
    t1, e1 = split_cases(cases, ratio=0.8, seed=1)
    t2, e2 = split_cases(cases, ratio=0.8, seed=1)
    assert [c.name for c in t1] == [c.name for c in t2]
    assert [c.name for c in e1] == [c.name for c in e2]
    assert len(t1) == 8 and len(e1) == 2
    assert len({c.name for c in t1 + e1}) == 10  # no overlap
    print("test_split_cases_deterministic: ok")


if __name__ == "__main__":
    test_stability_detects_flaky()
    test_stability_stable_pass()
    test_split_cases_deterministic()
    print("prompt-eval batch2 tests passed")

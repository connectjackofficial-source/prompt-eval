"""Tests for dict-based case loading."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import cases_from_dict, run


def _echo(prompt):
    return prompt


def test_cases_from_dict_builds():
    spec = [
        {"name": "t1", "prompt": "hello world", "check": "contains",
         "check_args": ["world"]},
        {"name": "t2", "prompt": "hello", "check": "length_between",
         "check_args": [3, 8]},
    ]
    cases = cases_from_dict(spec)
    assert [c.name for c in cases] == ["t1", "t2"]
    report = run(_echo, cases)
    assert report.passed == 2
    print("test_cases_from_dict_builds: ok")


def test_cases_from_dict_fails_fast():
    spec = [{"name": "bad", "prompt": "x", "check": "no_such_checker",
             "check_args": []}]
    try:
        cases_from_dict(spec)
        assert False, "should have raised"
    except ValueError as e:
        assert "unknown checker" in str(e)
    print("test_cases_from_dict_fails_fast: ok")


def test_cases_from_dict_detects_mismatch():
    spec = [
        {"name": "t1", "prompt": "hello world", "check": "contains",
         "check_args": ["mars"]},
    ]
    report = run(_echo, cases_from_dict(spec))
    assert report.failed == 1
    print("test_cases_from_dict_detects_mismatch: ok")


if __name__ == "__main__":
    test_cases_from_dict_builds()
    test_cases_from_dict_fails_fast()
    test_cases_from_dict_detects_mismatch()
    print("prompt-eval dict-spec tests passed")

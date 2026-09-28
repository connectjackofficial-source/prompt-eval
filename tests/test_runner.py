"""Tests for prompt-eval runner."""
from prompt_eval.runner import Case, contains, matches, not_contains, run


def test_contains_passes():
    fn = lambda p: f"answer: {p}"
    cases = [Case("t", "hi", contains("answer"))]
    report = run(fn, cases)
    assert report.passed == 1
    assert report.failed == 0
    print("test_contains_passes: ok")


def test_failure_counted():
    fn = lambda p: "nope"
    cases = [Case("t", "hi", contains("hello"))]
    report = run(fn, cases)
    assert report.failed == 1
    assert len(report.failures) == 1
    print("test_failure_counted: ok")


def test_not_contains():
    fn = lambda p: "hello world"
    cases = [Case("t", "hi", not_contains("error"))]
    report = run(fn, cases)
    assert report.passed == 1
    print("test_not_contains: ok")


if __name__ == "__main__":
    test_contains_passes()
    test_failure_counted()
    test_not_contains()
    print("prompt-eval tests passed")

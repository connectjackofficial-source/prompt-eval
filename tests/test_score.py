"""Test score property."""
from prompt_eval.runner import Case, contains, run


def test_score():
    fn = lambda p: "ok"
    cases = [Case("a", "x", contains("ok")), Case("b", "y", contains("no"))]
    report = run(fn, cases)
    assert report.passed == 1
    assert report.failed == 1
    assert report.score == 0.5
    print("test_score: ok")


if __name__ == "__main__":
    test_score()
    print("score test passed")

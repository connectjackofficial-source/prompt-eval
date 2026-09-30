"""More prompt-eval tests."""
from prompt_eval.runner import Case, length_between, run, contains


def test_length_between():
    fn = lambda p: "short"
    cases = [Case("len", "x", length_between(1, 10))]
    report = run(fn, cases)
    assert report.passed == 1
    print("test_length_between: ok")


def test_length_between_fail():
    fn = lambda p: "this is way too long for the limit"
    cases = [Case("len", "x", length_between(1, 5))]
    report = run(fn, cases)
    assert report.failed == 1
    print("test_length_between_fail: ok")


if __name__ == "__main__":
    test_length_between()
    test_length_between_fail()
    print("extra prompt-eval tests passed")

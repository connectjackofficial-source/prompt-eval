"""Tests for JSON report and run_and_save."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from prompt_eval.runner import Case, contains, run, run_and_save


def test_to_json():
    cases = [Case(name="ok", prompt="p1", check=contains("hi")),
             Case(name="bad", prompt="p2", check=contains("nope"))]
    report = run(lambda p: "hi there", cases)
    data = json.loads(report.to_json())
    assert data["passed"] == 1
    assert data["failed"] == 1
    assert data["score"] == 0.5
    assert len(data["failures"]) == 1
    assert data["failures"][0]["case"] == "bad"
    print("test_to_json: ok")


def test_run_and_save():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "report.json"
        cases = [Case(name="c", prompt="p", check=contains("ok"))]
        report = run_and_save(lambda p: "ok", cases, str(out))
        assert report.passed == 1
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["passed"] == 1
    print("test_run_and_save: ok")


if __name__ == "__main__":
    test_to_json()
    test_run_and_save()
    print("prompt-eval json tests passed")

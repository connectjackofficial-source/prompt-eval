# prompt-eval

> Tiny framework for evaluating prompts against test cases. Run your prompt
> function against a set of inputs, check the output, and get a pass/fail report.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

Prompt engineering is a guessing game until you have tests. `prompt-eval`
gives you the minimal loop: define cases, run your prompt, assert on the output.

## Install

```bash
git clone https://github.com/connectjackofficial-source/prompt-eval.git
```

## Usage

```python
from prompt_eval.runner import Case, contains, matches, run

def my_prompt(prompt: str) -> str:
    # call your LLM here
    return "..."

cases = [
    Case("upper", "say hi", contains("hello")),
    Case("format", "list users", matches(r"^\d+\. ")),
]

report = run(my_prompt, cases)
print(report.render())
```

## Built-in checkers

- `contains("text")`
- `matches(r"regex")`
- `not_contains("text")`
- `length_between(min, max)`
- `starts_with("prefix")`
- `ends_with("suffix")`

Write your own: any `(output: str) -> bool` callable.

## Per-case latency

`Report` tracks timing automatically:

```python
report = run(my_prompt, cases)
print(report.avg_latency_ms)  # mean ms per case
print(report.timings)         # per case, in order
```

## JSON reports (CI-friendly)

```python
from prompt_eval.runner import run_and_save

report = run_and_save(my_prompt, cases, "eval-report.json")
# {"passed": 3, "failed": 1, "score": 0.75, "avg_latency_ms": 42.0, ...}
```

## Cases from plain dicts

For CI pipelines that keep test cases in YAML/JSON instead of code:

```python
from prompt_eval.runner import cases_from_dict, run

spec = [
    {"name": "has-answer", "prompt": "what is 2+2?",
     "check": "contains", "check_args": ["4"]},
    {"name": "length", "prompt": "hi", "check": "length_between",
     "check_args": [3, 8]},
]
report = run(my_prompt, cases_from_dict(spec))
```

## Flaky detection & splits

LLM outputs are non-deterministic, so a single pass/fail can mislead.
Run each case several times and flag flip-floppers:

```python
from prompt_eval.runner import stability_check, split_cases

# [{"name": "has-answer", "passes": 3, "runs": 5, "rate": 0.6, "flaky": true}, ...]
print(stability_check(my_prompt, cases, runs=5))

train, test = split_cases(cases, ratio=0.8, seed=42)  # reproducible
```

## Tips

- Keep cases tiny and focused; one behavior per case.
- Run locally before you ship a prompt change — same idea as unit tests.
- Combine with `llm-trace` to also log cost and latency.

## License

MIT

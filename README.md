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

## Tips

- Keep cases tiny and focused; one behavior per case.
- Run locally before you ship a prompt change — same idea as unit tests.
- Combine with `llm-trace` to also log cost and latency.

## License

MIT

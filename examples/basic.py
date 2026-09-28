"""Example: evaluate a simple prompt function.

Run: python examples/basic.py
"""
from prompt_eval.runner import Case, contains, matches, run


def my_prompt(prompt: str) -> str:
    """Replace this with your actual prompt + LLM call.
    Here we echo to demonstrate the framework."""
    return f"Answer: {prompt.upper()}"


cases = [
    Case("upper", "hello", contains("HELLO")),
    Case("echo", "world", matches(r"ANSWER.*WORLD")),
]

report = run(my_prompt, cases)
print(report.render())

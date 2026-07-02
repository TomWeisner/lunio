# Extensions

This package contains optional work that sits outside the core rule-based safety
scorer.

## LLM Judge

`llm/judge.py` builds a constrained prompt for an LLM placement-safety judge.
`llm/runner.py` wraps that prompt in an OpenAI Responses API call and parses the
JSON decision.

These modules are intentionally separate from `lunio.models.rules_based`
because the main rules-based package is a deterministic, non-LLM baseline.

The LLM judge is best treated as an extension for ambiguous placements or future
experiments. It should be evaluated against human-labelled examples before it is
used for production decisions.

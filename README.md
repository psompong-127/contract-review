# Contract Reviewer

A rule-based contract review tool. It classifies each clauses and check against with a playbook. Then, it produces a report on findings.

No LLM. Every result is reproducible, and every rule is a line a lawyer can read and edit.

## What the output looks like

```
| Status | Count |
|---|---|
| FAIL   | 1 |
| REVIEW | 1 |
| MANUAL | 0 |
| PASS   | 1 |

## FAIL — HR-01 Working hours (severity: high)

**Finding:** Found 48 hours; does not meet the requirement of at most 40 hours.

> Working hours The working hours shall not exceed 48 hours per week.
```

Findings are sorted by urgency (fail → review → manual → pass), and each one quotes the clause it was drawn from.

## Quickstart

```bash
pip install -r requirements.txt
python src/review.py tests/fixtures/test_contract.txt
python -m pytest
```

Review your own contract and save the results:

```bash
python src/review.py my_contract.docx --out report.md --json findings.json
```

The process exits with code 1 when any rule fails, so it can gate an automated workflow.

The playbook behind these rules, with the rationale for each position, is in [docs/playbook.md](docs/playbook.md). The engine supports four check types — `presence`, `allowed_values`, `numeric_threshold`, and `manual` — so new rules can be added in YAML alone.

## Legal design decisions

**Rules live in YAML, not Python.** Legal positions change when the business's risk appetite changes; code changes when document formats change. Keeping them apart lets a lawyer raise the notice-period threshold in a one-line change that a reviewer can approve without reading Python.

**Uncertainty resolves to "review", never "pass".** If the engine cannot extract a number from a clause, it says so and hands the clause to a human. A false approval is the most expensive error in contract review; an unnecessary review costs thirty seconds.

**Judgment calls are routed, not faked.** Whether a non-compete is reasonable, or an indemnity balanced, requires legal judgment. The `manual` check type finds the clause, quotes it, and stops. Knowing the limit of deterministic tools is part of the design.

**Every finding quotes its evidence.** A reviewer must be able to verify the engine's reasoning in seconds, so each finding carries the clause text it was based on.

**Configuration is validated at the boundary.** A rule that names an unknown check type or unit produces an error message naming the rule and listing the valid options — not a stack trace. Both guards were added after real YAML typos during development.

## How it works

```
contract (.txt / .docx)
   │
   ▼
parser.py     split on numbered headings → classify each clause by keyword score
   │
   ▼
checkers.py   one function per check type; a dispatcher picks the right one per rule
   │
   ▼
report.py     findings sorted by urgency → Markdown or JSON
   │
   ▼
review.py     command-line entry point
```

- `rules/clause_keywords.yaml` maps clause types to keywords. Heading matches count triple, because headings are far more reliable than body text.
- `rules/employment_agreement.yaml` is the playbook in machine-readable form.
- `tests/` contains fixture contracts and 11 tests covering number extraction, each rule, and `.docx` parsing.

## Limitations

- Clause detection relies on numbered headings (1., 2., …). Contracts without numbering, or with nested sub-clauses, will be split poorly.
- Keyword classification is intentionally simple and can be misled by cross-references or by clauses that combine two subjects (for example, position and salary in one section).
- Number extraction handles common English drafting patterns — "forty (40) hours", "one month's notice", "30 days" but not every variation, and it ignores currency amounts.
- The engine cannot assess meaning. One-sided obligations, carve-outs, and conditional terms are outside its reach; see docs/DESIGN.md for what an LLM layer would add and how it should be evaluated.

## Project layout

```
contract-reviewer/
├── README.md
├── requirements.txt
├── docs/          playbook.md, DESIGN.md
├── rules/         employment_agreement.yaml, clause_keywords.yaml
├── src/           parser.py, checkers.py, report.py, review.py
├── tests/         fixtures/ and test files
└── examples/      sample_report.md, sample_report.json
```


## About

Built by a Thai-licensed lawyer with seven years in human rights due diligence and supply chain compliance, as a first legal-engineering project. The goal was to make legal judgment explicit, testable, and editable by the people who own it.

## License

MIT

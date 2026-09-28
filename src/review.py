import argparse
import sys
from pathlib import Path

from checkers import load_rules, run_rules
from parser import parse_contract
from report import to_json, to_markdown

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Rule-based contract reviewer")
    parser.add_argument("contract", help="Path to a .txt or .docx contract")
    parser.add_argument("--rules", default=ROOT / "rules" / "employment_agreement.yaml")
    parser.add_argument("--keywords", default=ROOT / "rules" / "clause_keywords.yaml")
    parser.add_argument("--out", help="Write the Markdown report to this file")
    parser.add_argument("--json", help="Write JSON findings to this file")
    args = parser.parse_args()

    clauses = parse_contract(args.contract, args.keywords)
    findings = run_rules(load_rules(args.rules), clauses)
    name = Path(args.contract).name

    markdown = to_markdown(findings, name)
    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
        print(f"Report written to {args.out}")
    else:
        print(markdown)

    if args.json:
        Path(args.json).write_text(to_json(findings, name), encoding="utf-8")
        print(f"JSON written to {args.json}")

    return 1 if any(f.status == "fail" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
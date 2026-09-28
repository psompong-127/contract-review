from pathlib import Path

from parser import read_document, split_into_clauses, load_keywords, classify_clause
from checkers import load_rules, check_presence

ROOT = Path(__file__).resolve().parent.parent


def parse(fixture_name):
    lines = read_document(ROOT / "tests" / "fixtures" / fixture_name)
    keywords = load_keywords(ROOT / "rules" / "clause_keywords.yaml")
    clauses = split_into_clauses(lines)
    for clause in clauses:
        clause.clause_type = classify_clause(clause, keywords)
    return clauses


def test_working_hours_clause_is_present_in_test_contract():
    clauses = parse("test contract.txt")
    rules = load_rules(ROOT / "rules" / "employment_agreement.yaml")
    finding = check_presence(rules[0], clauses)
    assert finding.status == "pass"
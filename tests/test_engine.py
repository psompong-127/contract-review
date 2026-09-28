from pathlib import Path

from parser import read_document, split_into_clauses, load_keywords, classify_clause

from checkers import load_rules, check_presence, check_allowed_values

ROOT = Path(__file__).resolve().parent.parent


def parse(fixture_name):
    lines = read_document(ROOT / "tests" / "fixtures" / fixture_name)
    keywords = load_keywords(ROOT / "rules" / "clause_keywords.yaml")
    clauses = split_into_clauses(lines)
    for clause in clauses:
        clause.clause_type = classify_clause(clause, keywords)
    return clauses

print(ROOT / "rules" / "employment_agreement.yaml")

def rule_by_id(rule_id):
    rules = load_rules(ROOT / "rules" / "employment_agreement.yaml")
    for rule in rules:
        if rule["id"] == rule_id:
            return rule
    raise ValueError(f"No rule with id {rule_id!r} in employment_agreement.yaml")

def test_job_assignment_clause_is_present_in_test_contract():
    finding = check_allowed_values(rule_by_id("PT-01"), parse("test_contract.txt"))
    assert finding.status == "pass"

def test_working_hours_clause_is_present_in_test_contract():
    finding = check_presence(rule_by_id("HR-01"), parse("test_contract.txt"))
    assert finding.status == "pass"

def test_termination_clause_is_present_in_test_contract():
    finding = check_presence(rule_by_id("TM-01"), parse("test_contract.txt"))
    assert finding.status == "pass"

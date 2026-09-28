from dataclasses import dataclass

import yaml

from parser import Clause, read_document, split_into_clauses, load_keywords, classify_clause


@dataclass
class Finding:
    rule_id: str
    rule_name: str
    status: str
    severity: str
    evidence: str
    explanation: str


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_clause(rule, clauses):
    for clause in clauses:
        if clause.clause_type == rule["clause_type"]:
            return clause
    return None


def check_presence(rule, clauses):
    clause = find_clause(rule, clauses)
    if clause is None:
        return Finding(
            rule_id=rule["id"],
            rule_name=rule["name"],
            status="fail",
            severity=rule["severity"],
            evidence="",
            explanation="No clause of this type was found in the contract.",
        )
    return Finding(
        rule_id=rule["id"],
        rule_name=rule["name"],
        status="pass",
        severity=rule["severity"],
        evidence=clause.text,
        explanation=f"Clause found under heading '{clause.heading}'.",
    )


if __name__ == "__main__":
    lines = read_document("tests/fixtures/test contract.txt")
    keywords = load_keywords("rules/clause_keywords.yaml")
    clauses = split_into_clauses(lines)
    for clause in clauses:
        clause.clause_type = classify_clause(clause, keywords)

    rules = load_rules("rules/employment_agreement.yaml")
    for rule in rules:
        finding = check_presence(rule, clauses)
        print(finding.rule_id, finding.status.upper(), "-", finding.explanation)
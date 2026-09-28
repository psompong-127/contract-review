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

def check_allowed_values(rule, clauses):
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
    text = clause.text.lower()
    matched = [value for value in rule["allowed"] if value.lower() in text]
    if matched:
        return Finding(
            rule_id=rule["id"],
            rule_name=rule["name"],
            status="pass",
            severity=rule["severity"],
            evidence=clause.text,
            explanation=f"Acceptable value found: {matched[0]}.",
        )
    return Finding(
        rule_id=rule["id"],
        rule_name=rule["name"],
        status=rule["on_violation"],
        severity=rule["severity"],
        evidence=clause.text,
        explanation="None of the acceptable values appear in the clause: "
        + ", ".join(rule["allowed"])
        + ".",
    )


CHECKERS = {
    "presence": check_presence,
    "allowed_values": check_allowed_values,
}

def run_rules(rules, clauses):
    findings = []
    for rule in rules:
        checker = CHECKERS[rule["check"]]
        findings.append(checker(rule, clauses))
    return findings

if __name__ == "__main__":
    lines = read_document("tests/fixtures/test contract.txt")
    keywords = load_keywords("rules/clause_keywords.yaml")
    clauses = split_into_clauses(lines)
    for clause in clauses:
        clause.clause_type = classify_clause(clause, keywords)

    rules = load_rules("rules/employment_agreement.yaml")
    for finding in run_rules(rules, clauses):
        print(finding.rule_id, finding.status.upper(), "-", finding.explanation)

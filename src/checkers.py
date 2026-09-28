import re
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

def check_numeric_threshold(rule, clauses):
    clause = find_clause(rule, clauses)
    if clause is None:
        return absent(rule)

    numbers = extract_numbers(clause.text, rule["unit"])
    if not numbers:
        return Finding(
            rule_id=rule["id"],
            rule_name=rule["name"],
            status="review",
            severity=rule["severity"],
            evidence=clause.text,
            explanation=f"Could not find a value in {rule['unit']}; manual check needed.",
        )

    if "min" in rule:
        value = min(numbers)
        ok = value >= rule["min"]
        requirement = f"at least {rule['min']} {rule['unit']}"
    else:
        value = max(numbers)
        ok = value <= rule["max"]
        requirement = f"at most {rule['max']} {rule['unit']}"

    return Finding(
        rule_id=rule["id"],
        rule_name=rule["name"],
        status="pass" if ok else rule["on_violation"],
        severity=rule["severity"],
        evidence=clause.text,
        explanation=f"Found {value:g} {rule['unit']}; "
        + ("meets" if ok else "does not meet")
        + f" the requirement of {requirement}.",
    )

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12,
    "fourteen": 14, "fifteen": 15, "twenty": 20, "thirty": 30,
    "forty": 40, "forty-five": 45, "forty-eight": 48, "sixty": 60,
    "ninety": 90,
}

UNIT_PATTERNS = {
    "hours": r"hours?",
    "days": r"(?:calendar\s+|business\s+|working\s+)?days?",
    "weeks": r"weeks?",
    "months": r"months?['’]?",
    "years": r"years?",
}


def normalize_numbers(text):
    words = "|".join(sorted(NUMBER_WORDS, key=len, reverse=True))
    text = re.sub(rf"\b(?:{words})\s*\((\d+)\)", r"\1", text, flags=re.IGNORECASE)
    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", str(number), text, flags=re.IGNORECASE)
    return text


def extract_numbers(text, unit):
    cleaned = normalize_numbers(text)
    pattern = rf"(\d+(?:\.\d+)?)\s*{UNIT_PATTERNS[unit]}(?![a-zA-Z])"
    return [float(n) for n in re.findall(pattern, cleaned, flags=re.IGNORECASE)]

CHECKERS = {
    "presence": check_presence,
    "allowed_values": check_allowed_values,
    "numeric_threshold": check_numeric_threshold,
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

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

@dataclass
class Clause:
    heading: str
    text: str
    position: int
    clause_type: str = "other"


HEADING_RE = re.compile(r"^\s*(\d+)\.\s+(.+)$")


def read_document(path):
    return Path(path).read_text(encoding="utf-8").splitlines()


def split_into_clauses(lines):
    clauses = []
    current = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        match = HEADING_RE.match(line)
        if match:
            if current is not None:
                clauses.append(current)
            body = match.group(2)
            heading = body.split(".")[0]
            current = Clause(heading=heading, text=body, position=len(clauses) + 1)
        elif current is not None:
            current.text = current.text + " " + line
    if current is not None:
        clauses.append(current)
    return clauses


def load_keywords(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def classify_clause(clause, keywords):
    heading = clause.heading.lower()
    text = clause.text.lower()
    scores = {}
    for clause_type, words in keywords.items():
        score = 0
        for word in words:
            if word in heading:
                score += 3
            if word in text:
                score += 1
        if score > 0:
            scores[clause_type] = score
    if scores:
        return max(scores, key=scores.get)
    return "other"

if __name__ == "__main__":
    lines = read_document("tests/fixtures/test contract.txt")
    keywords = load_keywords("rules/clause_keywords.yaml")
    for clause in split_into_clauses(lines):
        clause.clause_type = classify_clause(clause, keywords)
        print(clause.position, "|", clause.heading, "→", clause.clause_type)
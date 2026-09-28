import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Clause:
    heading: str
    text: str
    position: int


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


if __name__ == "__main__":
    lines = read_document("tests/fixtures/test contract.txt")
    for clause in split_into_clauses(lines):
        print(clause.position, "|", clause.heading, "|", clause.text[:60])
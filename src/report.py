import json
from dataclasses import asdict

STATUS_ORDER = {"fail": 0, "review": 1, "manual": 2, "pass": 3}

STATUS_LABELS = {
    "fail": "FAIL",
    "review": "REVIEW",
    "manual": "MANUAL",
    "pass": "PASS",
}


def sort_findings(findings):
    return sorted(findings, key=lambda f: STATUS_ORDER[f.status])


def to_markdown(findings, contract_name):
    findings = sort_findings(findings)
    lines = [f"# Contract review: {contract_name}", ""]

    lines += ["| Status | Count |", "|---|---|"]
    for status, label in STATUS_LABELS.items():
        count = sum(1 for f in findings if f.status == status)
        lines.append(f"| {label} | {count} |")
    lines.append("")

    for f in findings:
        lines.append(f"## {STATUS_LABELS[f.status]} — {f.rule_id} {f.rule_name} (severity: {f.severity})")
        lines.append("")
        lines.append(f"**Finding:** {f.explanation}")
        lines.append("")
        if f.evidence:
            lines.append(f"> {f.evidence}")
            lines.append("")
    return "\n".join(lines)


def to_json(findings, contract_name):
    return json.dumps(
        {"contract": contract_name, "findings": [asdict(f) for f in sort_findings(findings)]},
        indent=2,
        ensure_ascii=False,
    )
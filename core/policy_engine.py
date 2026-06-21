import yaml

with open("config/policies.yaml") as f:
    POLICY = yaml.safe_load(f)


def evaluatePolicy(risk, analysis):
    print("POLICY INPUT:", risk)
    print("POLICY ANALYSIS:", analysis)

    score = float(risk["risk_score"])

    severity = risk.get("severity", "low")

    category = analysis.get(
        "risk_category",
        ""
    )

    # 1. Blocked categories
    if category in POLICY["blocked_categories"]:
        return "BLOCK"

    # 2. Blocked severities
    if severity in POLICY["blocked_severities"]:
        return "BLOCK"

    # 3. Risk threshold
    if score >= POLICY["max_risk_score"]:
        return "BLOCK"

    # 4. Approval-required categories
    if category in POLICY["approval_required"]:
        return "PENDING"

    # 5. Risk-based approval
    if score >= POLICY["approval_threshold"]:
        return "PENDING"

    return "ALLOW"
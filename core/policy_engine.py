import yaml

with open("config/policies.yaml") as f:
    POLICY = yaml.safe_load(f)


def evaluatePolicy(risk, analysis):
    print("POLICY INPUT:", risk)
    print("POLICY ANALYSIS:", analysis)

    score = float(risk["risk_score"])
    severity = risk.get("severity", "low")
    category = analysis.get("risk_category", "")

    # 1. Explicitly blocked categories
    if category in POLICY["blocked_categories"]:
        return "BLOCK"

    # 2. Critical severity always blocks
    if severity in POLICY["blocked_severities"]:
        return "BLOCK"

    # 3. High risk score always blocks
    if score >= POLICY["max_risk_score"]:
        return "BLOCK"

    # 4. Categories requiring Human-in-the-Loop
    if category in POLICY["approval_required"]:
        return "PENDING"

    # 5. Medium severity requires Human-in-the-Loop
    if severity == "medium":
        return "PENDING"

    # 6. Configurable approval severities
    if severity in POLICY.get("approval_severities", []):
        return "PENDING"

    # 7. Score-based Human-in-the-Loop
    if score >= POLICY["approval_threshold"]:
        return "PENDING"

    # 8. Everything else is safe
    return "ALLOW"
import json
from langchain_ollama import ChatOllama
from helper import extract_json

riskLLM = ChatOllama(model="gemma3:1b")

RISK_PROMPT = """
You are Aegis GitHub Risk Engine.

Your job is to evaluate the security risk of a GitHub operation.

You will receive:

1. The user's intended action.
2. Repository context.
3. Changed files.
4. Secret scan results.
5. Current branch.

Use ONLY the supplied evidence.

Do NOT invent information.

Rules:

- If .env or credentials are detected:
  risk_score >= 0.95

- If secrets are detected:
  risk_score >= 0.90

- If pushing only documentation:
  risk_score <= 0.20

- If pushing code to main without secrets:
  risk_score between 0.30 and 0.60

- risk_score MUST be between 0.0 and 1.0.

Return ONLY JSON:

{
    "risk_score": 0.0,
    "reason": ""
}
"""

def assess_risk(analysis,context):
    print("RISK INPUT: ",analysis)
    response = riskLLM.invoke(
        [
            {
                "role": "system",
                "content": RISK_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "action": analysis,
                        "repository_context": context
                    },
                    indent=2
                )
            }
        ]
    )
    print("\n=== RISK AGENT RAW RESPONSE ===")
    print(response.content)
    print("===============================\n")

    risk = extract_json(response.content)
    print("RISK AGENT: ",risk)
    if risk is None:
        return {
            "risk_score": 1.0,
            "severity": "critical",
            "reason": "Unable to assess risk"
        }

    risk_score = float(risk.get("risk_score", 0))
    risk_score = max(0.0, min(1.0, risk_score))
    risk["risk_score"] = risk_score

    if risk_score >= 0.9:
        severity = "critical"
    elif risk_score >= 0.7:
        severity = "high"
    elif risk_score >= 0.4:
        severity = "medium"
    else:
        severity = "low"

    risk["severity"] = severity

    return risk
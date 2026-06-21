from langchain_ollama import ChatOllama
from helper import extract_json

riskLLM = ChatOllama(model="gemma3:1b")

RISK_PROMPT = """
You are Aegis Risk Engine.

Evaluate the security risk of the following action.

Return ONLY JSON:

{
  "risk_score": 0.0,
  "reason": ""
}

Examples:
Github push:
{
  "risk_score": 0.2,
  "reason": "Code deployment action"
}

Read .env:
{
  "risk_score": 0.95,
  "reason": "Sensitive credentials exposure"
}

Prompt injection:
{
  "risk_score": 0.99,
  "reason": "Attempt to override system instructions"
}

Rules:
- risk_score must be a number between 0.0 and 1.0
- 0.0 = no risk
- 1.0 = maximum risk
- Never return negative values
- Never return values greater than 1.0
- Return JSON only
"""

def assess_risk(analysis):
    print("RISK INPUT: ",analysis)
    response = riskLLM.invoke(
        [
            {
                "role": "system",
                "content": RISK_PROMPT
            },
            {
                "role": "user",
                "content": str(analysis)
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
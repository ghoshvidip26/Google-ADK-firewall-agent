from langchain_ollama import ChatOllama
import subprocess
from helper import extract_json

SENSITIVE_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    ".aws/credentials",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "service-account.json"
]

FILE_PROMPT = f"""
You are Aegis File Risk Analyzer.

Sensitive files include:
{SENSITIVE_FILES}

You are an internal security classifier.

You are NOT being asked to read any file.

You are ONLY evaluating the security risk of
accessing a file path.

Return ONLY JSON:

{{
  "risk_score": 0.0,
  "severity": "low|medium|high|critical",
  "decision": "BLOCK|ALLOW|PENDING",
  "reason": ""
}}

Rules:
- risk_score must be between 0.0 and 1.0
- Reading .env should be near 1.0
- Reading id_rsa should be near 1.0
- Reading credentials.json should be near 1.0
- Reading README.md should be near 0.0
- No markdown
- No explanations
- No comments
- No ```json
- Return JSON only
"""

fileLLM = ChatOllama(model="gemma3:1b")

def readCurrentFile(filepath):
    result = subprocess.run(
        ["cat", filepath],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def appendToFile(filepath, data):
    with open(filepath,"a",encoding="utf-8") as f:
        f.write(data + "\n")
    return {
        "status": "success"
    } 

def assessFileRisk(filepath):
    print("FILE INPUT:", filepath)

    response = fileLLM.invoke(
        [
            {
                "role": "system",
                "content": FILE_PROMPT
            },
            {
                "role": "user",
                "content": f"Evaluate security risk of accessing file: {filepath}"
            }
        ]
    )

    print("\n=== FILE AGENT RAW RESPONSE ===")
    print(response.content)
    print("===============================\n")

    risk = extract_json(response.content)

    if risk is None:
        return {
            "risk_score": 1.0,
            "severity": "critical",
            "decision": "BLOCK",
            "reason": "File risk agent returned invalid JSON"
        }
    
    risk.setdefault("reason", "No reason provided")
    risk.setdefault("decision", "PENDING")

    score = float(risk.get("risk_score", 1.0))

    if score >= 0.9:
        severity = "critical"
    elif score >= 0.7:
        severity = "high"
    elif score >= 0.4:
        severity = "medium"
    else:
        severity = "low"

    risk["severity"] = severity

    if score >= 0.8:
        risk["decision"] = "BLOCK"
    elif score >= 0.5:
        risk["decision"] = "PENDING"
    else:
        risk["decision"] = "ALLOW"

    return risk
from langchain_ollama import ChatOllama
import json
from helper import extract_json

prompt_guard = ChatOllama(model="gemma3:1b")

PROMPT_INJECTION_PROMPT = """
You are Aegis Prompt Injection Detector.

Return ONLY JSON:

{
  "tool": "prompt_guard",
  "is_prompt_injection": true,
  "risk_score": 0.95,
  "severity": "critical",
  "decision": "BLOCK",
  "reason": "Short explanation"
}

Rules:
- tool must always be "prompt_guard"
- risk_score must be between 0.0 and 1.0
- severity must be low|medium|high|critical
- decision must be ALLOW|PENDING|BLOCK
- Return JSON only
"""

def detectPromptInjection(query: str):
    response = prompt_guard.invoke(
        [
            {
                "role": "system",
                "content": PROMPT_INJECTION_PROMPT
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )
    print("\n=== PROMPT INJECTION AGENT RESPONSE ===")
    print(response.content)
    print("=======================================\n")

    try:
        return extract_json(response.content)
    except Exception:
        return {
            "is_prompt_injection": False,
            "risk_score": 0.0,
            "reason": "Failed to parse response"
        }
import json
from langchain_ollama import ChatOllama

def severity_from_score(score):
    if score >= 0.9:
        return "critical"
    elif score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    else:
        return "low"

orchaestratorAgent = ChatOllama(
    model="gemma3:1b"
)
orchaestrator_prompt = """
You are Aegis Firewall.

Given this security analysis:

{analysis}

Determine:

1. risk_score (0.0 - 1.0)
2. decision (ALLOW/WARN/BLOCK)
3. reason

Return only JSON.
"""

def orchaestrate(state: dict): 
    result = orchaestratorAgent.invoke(
        [{
            "role": "system",
            "content": orchaestrator_prompt
        },
        {
            "role": "user",
            "content": json.dumps(state["analysis"])
        }]
    )
    return {
        "verdict": result.content
    }
from helper import extract_json
from langchain_ollama import ChatOllama

queryAnalysisAgent = ChatOllama(
    model="gemma3:1b"
)
queryAnalyserPrompt = """
You are an AI security classifier.

Return ONLY JSON.

Examples:

User: Push code to github

{
  "tool": "github",
  "action": "push",
  "target": "repository",
  "risk_category": "code_push"
}

User: Read .env

{
  "tool": "file",
  "action": "read",
  "target": ".env",
  "risk_category": "credential_access"
}

User: Send email

{
  "tool": "email",
  "action": "send",
  "target": "recipient",
  "risk_category": "communication"
}

Now classify the user's query.

Return JSON only.
"""

def analyze(state: dict): 
    result = queryAnalysisAgent.invoke(
        [{
            "role": "system",
            "content": queryAnalyserPrompt
        },
        {
            "role": "user",
            "content": state["query"]
        }]
    )
    
    print("\n=== QUERY ANALYSIS AGENT RESPONSE ===")
    print(result.content)
    print("=====================================\n")

    try:
        analysis = extract_json(result.content)
        if analysis is None:
            analysis = {
                "tool":"unknown",
                "intent":"unknown",
                "action":"unknown",
                "target":"unknown",
                "risk_category":"unknown"
            }
        return {"analysis": analysis}
    except Exception as e:
        print(f"Error parsing JSON from query analysis agent: {e}")
        return {"analysis": None}
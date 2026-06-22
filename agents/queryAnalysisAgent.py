from helper import extract_json
from langchain_ollama import ChatOllama
from core.prompt_guard import PROMPT_INJECTION_PATTERNS

SHELL_PREFIXES = [
    "ls",
    "pwd",
    "echo",
    "rm",
    "cat",
    "grep",
    "find",
    "curl",
    "wget",
    "ssh",
    "scp",
    "git",
    "npm",
    "pip",
    "brew",
    "yarn",
    "pnpm"
]

queryAnalysisAgent = ChatOllama(
    model="gemma3:1b"
)
queryAnalyserPrompt = """
You are an AI security classifier.

Return ONLY JSON.
{
    "tool": "shell|github|prompt_guard",
    "action": "execute|push|read|send|analyze",
    "target": "full target or command",
    "risk_category": "string"
}

Examples:
echo hello
{
    "tool":"shell",
    "action":"execute",
    "target":"echo hello",
    "risk_category":"shell_command_execution"
}

rm -rf /
{
    "tool":"shell",
    "action":"execute",
    "target":"rm -rf /",
    "risk_category":"shell_command_execution"
}

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
    query = state["query"].strip()
    query_lower = query.lower()
    print("RAW QUERY:", query)
    print("LOWER QUERY:", query.lower())

    if any(pattern in query_lower for pattern in PROMPT_INJECTION_PATTERNS):
        return {
            "analysis":{
                "tool": "prompt_guard",
                "action": "analyze",
                "target": query,
                "risk_category": "prompt_injection"
            }
        }

    if any(query_lower.startswith(cmd) for cmd in SHELL_PREFIXES):
        return {
            "analysis":{
                "tool": "shell",
                "action": "execute",
                "target": query,
                "risk_category": "shell_command_execution"
            }
        }

    if ".env" in query_lower: 
        return {
            "analysis":{
                "tool": "file",
                "action": "read",
                "target": ".env",
                "risk_category":"credential_access"
            }
        }
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
        print("PARSED ANALYSIS: ",analysis)
        return {"analysis": analysis}
    except Exception as e:
        print(f"Error parsing JSON from query analysis agent: {e}")
        return {"analysis": None}
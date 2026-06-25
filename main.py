from tools.tools import buildGithubContext
from dashboard import showDashboard
from agents.queryAnalysisAgent import analyze
from core.policy_engine import evaluatePolicy
from core.logger import logEvent
from core.risk_agent import assess_risk
from tools.tools import pushCode
from core.shell_risk import assess_shell_command
from core.prompt_guard import detectPromptInjection
from core.file_engine import assessFileRisk
from tools.cache import setDataToCache,getDataFromCache,createCacheKey

def main():

    query = input("Enter query: ")
    cacheKey = createCacheKey(query)
    cached = getDataFromCache(cacheKey)

    if cached:
        print("Cache Hit")
        analysis = cached["analysis"]
        risk = cached["risk"]
        decision = cached["decision"]
    else:
        print("Cache Miss")
        analysis = analyze({
            "query": query
        })
        tool = analysis["analysis"]["tool"]
        if tool=="shell": 
            risk = assess_shell_command(
                query
            )
        elif tool=="github":
            context = buildGithubContext()
            risk = assess_risk(
                analysis["analysis"],context
            )

        elif tool=="prompt_guard":
            risk = detectPromptInjection(
                analysis["analysis"]["target"]
            )

        elif tool=="file":
            risk = assessFileRisk(
                analysis["analysis"]["target"]
            )
        else:
            risk = {
                "risk_score": 1.0,
                "severity": "critical",
                "decision": "BLOCK",
                "reason": "Unknown tool detected"
            }
        decision = evaluatePolicy(
            risk,
            analysis["analysis"]
        )
        setDataToCache(cacheKey,{
            "analysis": analysis,
            "risk": risk,
            "decision": decision
        })
    print("ANALYSIS OBJECT:", analysis)    
    
    showDashboard(
        query=query,
        # tool=analysis["analysis"]["tool"],
        tool=analysis["analysis"].get("tool", "unknown"),
        risk_score=risk["risk_score"],
        severity=risk["severity"],
        decision=decision,
        reason=risk.get("reason", "No reason provided")
    )
    
    if decision=="PENDING":
        approval = input("\n[AEGIS] Approve action? (y/n): ").strip().lower()
        if approval=="y":
            decision="ALLOW"
        else:
            decision="BLOCK"
    
    if decision=="ALLOW" and analysis["analysis"]["tool"]=="github":
        # pushCode(
        #     repo=analysis["analysis"]["repo"],
        #     branch=analysis["analysis"]["branch"]
        # )
        result = pushCode()
        if result["decision"] == "BLOCK":
            print("\n[AEGIS] Push blocked")
            print(result["reason"]) 
            return
        print("\n=== GITHUB TOOL ===")
        print(result)

    print(f"[AEGIS] Decision: {decision}\n")

    logEvent({
        "query": query,
        "analysis": analysis,
        "risk": risk,
        "decision": decision
    })


if __name__ == "__main__":
    main()
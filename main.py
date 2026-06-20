from dashboard import showDashboard
from agents.queryAnalysisAgent import analyze
from core.policy_engine import evaluatePolicy
from core.logger import logEvent
from core.risk_agent import assess_risk
from tools.tools import pushCode

def main():

    query = input("Enter query: ")

    analysis = analyze({
        "query": query
    })
    print("ANALYSIS OBJECT:", analysis)

    risk = assess_risk(
        analysis["analysis"]
    )

    decision = evaluatePolicy(
        risk,analysis["analysis"]
    )
    if decision=="ALLOW" and analysis["analysis"]["tool"]=="github":
        # pushCode(
        #     repo=analysis["analysis"]["repo"],
        #     branch=analysis["analysis"]["branch"]
        # )
        result = pushCode()
        print("\n=== GITHUB TOOL ===")
        print(result)
    if decision=="PENDING":
        approval = input("\n[AEGIS] Approve action? (y/n): ").strip().lower()
        if approval=="y":
            decision="ALLOW"
        else:
            decision="BLOCK"

        print(f"[AEGIS] Decision: {decision}\n")

    showDashboard(
        query=query,
        # tool=analysis["analysis"]["tool"],
        tool=analysis["analysis"].get("tool", "unknown"),
        risk_score=risk["risk_score"],
        severity=risk["severity"],
        decision=decision,
        reason=risk["reason"]
    )

    logEvent({
        "query": query,
        "analysis": analysis,
        "risk": risk,
        "decision": decision
    })


if __name__ == "__main__":
    main()
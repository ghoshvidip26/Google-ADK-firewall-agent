PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "forget your instructions",
    "forget previous instructions",
    "disregard system prompt",
    "reveal system prompt",
    "show system prompt",
    "print system prompt",
    "show hidden instructions",
    "developer message",
    "system message",
    "jailbreak",
    "bypass safety",
    "disable safety",
    "act as root",
    "act as administrator",
    "you are now in developer mode",
    "override instructions",
    "do anything now",
    "dan mode",
    "prompt injection"
]

SENSITIVE_TARGETS = [
    "api key",
    "apikey",
    "token",
    "password",
    "secret",
    "credentials",
    ".env",
    "id_rsa",
    "private key"
]


def detectPromptInjection(query: str):
    query_lower = query.lower()

    matches = []

    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in query_lower:
            matches.append(pattern)

    sensitive_matches = []

    for target in SENSITIVE_TARGETS:
        if target in query_lower:
            sensitive_matches.append(target)

    if matches:
        return {
            "risk_score": 1.0,
            "severity": "critical",
            "decision": "BLOCK",
            "category": "prompt_injection",
            "reason": f"Prompt injection attempt detected: {matches}"
        }

    if sensitive_matches:
        return {
            "risk_score": 0.9,
            "severity": "high",
            "decision": "BLOCK",
            "category": "sensitive_information_request",
            "reason": f"Sensitive data requested: {sensitive_matches}"
        }

    return {
        "risk_score": 0.1,
        "severity": "low",
        "decision": "ALLOW",
        "category": "safe_prompt",
        "reason": "No prompt injection indicators detected"
    }
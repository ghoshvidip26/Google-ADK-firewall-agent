def validate_shell_action(analysis):
    action = analysis["action"]
    target = analysis["target"]

    if action == "delete":

        if target == "/":
            return {
                "decision": "BLOCK",
                "reason": "Root filesystem deletion"
            }

        if target == "~":
            return {
                "decision": "BLOCK",
                "reason": "Home directory deletion"
            }

        if target == ".git":
            return {
                "decision": "PENDING",
                "reason": "Repository metadata deletion"
            }

        if target == ".venv":
            return {
                "decision": "PENDING",
                "reason": "Virtual environment deletion"
            }

    return {
        "decision": "ALLOW"
    }
LOW_RISK_COMMANDS = [
    "pwd",
    "ls",
    "ls -la",
    "whoami",
    "date",
    "uptime",
    "hostname",
    "uname",
    "uname -a",
    "which",
    "echo",
    "history",
    "env",
    "printenv",
    "git status",
    "git log",
    "git branch",
    "git remote -v",
    "git diff",
    "git show",
    "git reflog",
    "cat",
    "head",
    "tail",
    "less",
    "find",
    "grep",
    "du",
    "df",
    "tree"
]

MEDIUM_RISK_COMMANDS = [
    "touch",
    "mkdir",
    "cp",
    "mv",
    "ln",
    "npm install",
    "npm update",
    "yarn install",
    "pnpm install",
    "pip install",
    "pip uninstall",
    "brew install",
    "brew upgrade",
    "git add",
    "git commit",
    "git push",
    "git pull",
    "git stash",
    "git checkout",
    "git switch",
    "git merge",
    "curl",
    "wget",
    "scp",
    "ssh",
    "rsync"
]

HIGH_RISK_PATTERNS = {
    # Credential access
    "cat .env": "credential_access",
    ".env": "credential_access",
    "id_rsa": "credential_access",
    "id_ed25519": "credential_access",
    ".aws/credentials": "credential_access",
    "/etc/shadow": "credential_access",

    # Dangerous deletion
    "rm -rf /": "filesystem_delete",
    "rm -rf ~": "filesystem_delete",
    "rm -rf *": "filesystem_delete",
    "find . -delete": "filesystem_delete",

    # Privilege escalation
    "sudo rm": "privilege_escalation",
    "sudo chmod": "privilege_escalation",
    "sudo chown": "privilege_escalation",
    "sudo su": "privilege_escalation",

    # System disruption
    "shutdown": "system_disruption",
    "reboot": "system_disruption",
    "poweroff": "system_disruption",
    "kill -9": "system_disruption",
    "killall": "system_disruption",
    "pkill": "system_disruption",

    # Reverse shells
    "nc -e": "remote_access",
    "netcat -e": "remote_access",
    "bash -i": "remote_access",
    "socat": "remote_access",

    # Exfiltration
    "curl -x post": "data_exfiltration",
    "wget --post-data": "data_exfiltration"
}

def assess_shell_command(command: str):
    command = command.lower().strip()

    # HIGH
    for pattern, category in HIGH_RISK_PATTERNS.items():
        if pattern in command:
            return {
                "risk_score": 1.0,
                "severity": "critical",
                "decision": "BLOCK",
                "category": category,
                "reason": "Dangerous shell command detected"
            }
    # Special rm cases
    if command.startswith("rm"):
        if any(
            target in command
            for target in [
                ".git",
                "node_modules",
                "build",
                "dist",
                "__pycache__"
            ]
        ):
            return {
                "risk_score": 0.5,
                "severity": "medium",
                "decision": "PENDING",
                "category": "destructive_operation",
                "reason": "Destructive operation detected"
            }

        return {
            "risk_score": 0.5,
            "severity": "medium",
            "decision": "PENDING",
            "category": "file_deletion",
            "reason": "File deletion requested"
        }

    # MEDIUM
    for cmd in MEDIUM_RISK_COMMANDS:
        if command.startswith(cmd):
            return {
                "risk_score": 0.5,
                "severity": "medium",
                "decision": "PENDING",
                "category": "modification",
                "reason":"Command modifies system state"
            }

    # LOW
    for cmd in LOW_RISK_COMMANDS:
        if command.startswith(cmd):
            return {
                "risk_score": 0.1,
                "severity": "low",
                "decision": "ALLOW",
                "category": "read_only",
                "reason":"Read-only shell command"
            }

    return {
        "risk_score": 0.7,
        "severity": "high",
        "decision": "PENDING",
        "category": "unknown_command",
        "reason": "Unknown shell command requires human review"
    }
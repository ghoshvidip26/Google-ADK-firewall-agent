import subprocess
import os
import math
from collections import Counter
import re

def calculateEntropy(text):
    if not text:
        return 0
    counts = Counter(text)
    probs = [count / len(text) for count in counts.values()]
    return -sum(
        p * math.log2(p)
        for p in probs
    )

def looks_like_secret(value):
    if len(value) < 20:
        return False
    entropy = calculateEntropy(value)
    return entropy > 3.5

DANGEROUS_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "node_modules",
    "__pycache__",
    "venv",
    "build",
    "dist"
]

def getCurrentBranch():
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def getRemoteRepo():
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def getChangedFiles():
    result = subprocess.run(["git", "status", "--porcelain"],capture_output=True,text=True)
    files= []
    for line in result.stdout.splitlines():
        files.append(line.split(" ")[-1])
    return files

def getGitDiff():
    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True
    )
    return result.stdout

def scanSecrets():
    findings = []
    diff = getGitDiff()
    for line in diff.splitlines():
        if not line.startswith("+"):
            continue

        if line.startswith("+++"):
            continue

        if "process.env" in line:
            continue

        if "os.getenv" in line:
            continue

        if "os.environ" in line:
            continue

        match = re.search(
            r'=\s*["\']([^"\']+)["\']',
            line
        )

        if not match:
            continue

        value = match.group(1)

        if (len(value) > 20 and looks_like_secret(value)):
            findings.append({
                "line": line.strip()
            })

    return findings        

def scanFiles(files):
    detected = []
    for file in files:
        filename = os.path.basename(file)
        if filename in DANGEROUS_FILES:
            detected.append(file)
    return detected

def executeShell(command):
    return {
        "tool": "shell",
        "action": command
    }

def readFile(path): 
    return {
        "tool": "file",
        "path": path
    }

def buildGithubContext():
    return {
        "repo": getRemoteRepo(),
        "branch": getCurrentBranch(),
        "changed_files": getChangedFiles(),
        "git_diff": getGitDiff(),
        "dangerous_files": scanFiles(getChangedFiles()),
        "secret_findings": scanSecrets()
    }

def pushCode(): 
    files = getChangedFiles()
    dangerous_files = scanFiles(files)
    repo = getRemoteRepo()
    branch = getCurrentBranch()
    print("\n=== CURRENT STATE ===")
    print(f"Repo: {repo}")
    print(f"Branch: {branch}")
    print(f"Files: {files}")
    
    print("\n[AEGIS] Scanning files...")
    print(files)
    print("\n[AEGIS] Looking for secrets...")
    
    secret_findings = scanSecrets()
    if dangerous_files:
        return {
            "decision": "BLOCK",
            "risk_score": 0.95,
            "reason": f"Sensitive files detected: {dangerous_files}"
        }
    if secret_findings:
        return {
            "decision": "BLOCK",
            "risk_score": 0.95,
            "reason": f"Secret patterns detected: {secret_findings}"
        }
    subprocess.run(["git", "add", "."])
    commitMessage = f"Aegis commit to {branch}"
    subprocess.run(["git", "commit", "-m", commitMessage],check=True,text=True)

    subprocess.run(["git", "push","origin",branch])
    print("Successfully pushed code")
    return {
        "decision": "ALLOW",
        "tool": "github",
        "repo": repo,
        "branch": branch
    }

def send_email(to, content):
    return {
        "tool": "email",
        "recipient": to,
        "content": content
    }    
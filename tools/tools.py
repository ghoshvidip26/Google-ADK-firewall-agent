import subprocess
import os

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
SECRET_PATTERNS = [
    "api_key=",
    "apikey=",
    "secret=",
    "token=",
    "private_key=",
    "aws_access_key_id",
    "aws_secret_access_key",
    "bearer "
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

def scanSecrets(files):
    findings = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in SECRET_PATTERNS:
                    if pattern.lower() in content:
                        findings.append({
                            "file": file,
                            "pattern": pattern,
                            "risk_score": 1.0
                        })
        except:
            pass
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
    
    secret_findings = scanSecrets(files)
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

    if commitMessage.returncode!=0:
        return {
            "decision": "BLOCK",
            "risk_score": 0.95,
            "reason": "Commit failed"
        }

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
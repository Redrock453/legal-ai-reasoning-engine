"""Repo tool wrapper for open-code runtime."""
import subprocess


def repo_tool(task: str) -> str:
    """
    Minimal repo interaction tool.
    READ-ONLY first stage.
    """
    task = task.lower().strip()
    
    if "status" in task:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd="/root/backend"
        )
        return result.stdout or "(no changes)"
    
    if "diff" in task or "changed" in task:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            cwd="/root/backend"
        )
        return result.stdout or "(no changes)"
    
    if "log" in task or "recent" in task:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            cwd="/root/backend"
        )
        return result.stdout or "(no commits)"
    
    if "files" in task or "list" in task:
        result = subprocess.run(
            ["ls", "-la"],
            capture_output=True,
            text=True,
            cwd="/root/backend"
        )
        return result.stdout
    
    if "branch" in task:
        result = subprocess.run(
            ["git", "branch", "-v"],
            capture_output=True,
            text=True,
            cwd="/root/backend"
        )
        return result.stdout or "(no branch)"
    
    return "NO_MATCHING_ACTION"


if __name__ == "__main__":
    print(repo_tool("show status"))
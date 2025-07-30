import requests
from urllib.parse import urlparse

def get_pr_diff(repo_url: str, pr_number: int, github_token: str = None):
    """
    Fetch diff of a pull request using GitHub's REST API.
    Returns a list of files with filename and patch (diff).
    """
    print(" here to get pr diff")
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) != 2:
        raise ValueError("Invalid GitHub repo URL")

    owner, repo = path_parts
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"token {github_token}" if github_token else None
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers={k: v for k, v in headers.items() if v})
    response.raise_for_status()

    return [
        {
            "filename": f["filename"],
            "diff": f.get("patch", "")
        }
        for f in response.json()
    ]

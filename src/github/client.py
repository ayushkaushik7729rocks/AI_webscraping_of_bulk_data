import json
import re


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self, crawler):
        self.crawler = crawler

    async def get_repository(
        self,
        owner,
        repo
    ):

        url = (
            f"{self.BASE_URL}/repos/"
            f"{owner}/{repo}"
        )

        result = await self.crawler.fetch(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            }
        )

        if result["status"] != 200:
            raise RuntimeError(
                f"GitHub repository request failed: "
                f"{result['status']} - {result['error']}"
            )

        return json.loads(
            result["html"]
        )

    async def get_star_count(
        self,
        owner,
        repo
    ):

        repository = await self.get_repository(
            owner,
            repo
        )

        return repository["stargazers_count"]

    @staticmethod
    def parse_repository_url(
        github_url
    ):

        pattern = (
            r"https?://github\.com/"
            r"([^/]+)/([^/#?]+)"
        )

        match = re.match(
            pattern,
            github_url
        )

        if not match:
            raise ValueError(
                f"Invalid GitHub repository URL: "
                f"{github_url}"
            )

        owner = match.group(1)
        repo = match.group(2)

        if repo.endswith(".git"):
            repo = repo[:-4]

        return owner, repo

    async def get_repository_metadata(self, github_url):
        owner, repo = self.parse_repository_url(github_url)

        repository = await self.get_repository(owner, repo)

        return {
            "owner": owner,
            "repo": repo,
            "url": github_url,
            "name": repository.get("name"),
            "full_name": repository.get("full_name"),
            "description": repository.get("description"),
            "stargazers_count": repository.get("stargazers_count"),
            "html_url": repository.get("html_url"),
        }
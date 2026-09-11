class RepositoryResolver:

    def resolve(self, paper):
        """
        Try to resolve a research paper to a GitHub repository.

        Returns:
            {
                "github_url": str | None,
                "confidence": float,
                "evidence": str | None
            }
        """

        github_url = paper.get("github_url")

        if github_url:
            return {
                "github_url": github_url,
                "confidence": 1.0,
                "evidence": "explicit_source"
            }

        return {
            "github_url": None,
            "confidence": 0.0,
            "evidence": None
        }
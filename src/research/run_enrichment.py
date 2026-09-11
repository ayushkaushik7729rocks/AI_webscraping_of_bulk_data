import asyncio
import json

from src.crawler.base import AsyncCrawler
from src.extraction.record import build_research_paper_record
from src.github.client import GitHubClient
from src.research.arxiv import ArxivClient
from src.research.repository_matcher import RepositoryMatcher


async def enrich_paper(crawler, paper):
    """
    Enrich one arXiv paper with a verified GitHub repository
    and its current GitHub star count.
    """

    arxiv_client = ArxivClient(crawler)
    github_client = GitHubClient(crawler)
    matcher = RepositoryMatcher()

    # ---------------------------------------------------------
    # 1. Discover GitHub repositories from the arXiv paper page
    # ---------------------------------------------------------
    candidate_urls = await arxiv_client.get_github_urls(
        paper["paper_url"]
    )

    print("\n=== GITHUB CANDIDATES ===")

    for url in candidate_urls:
        print(url)

    print(
        f"\nTotal candidates: {len(candidate_urls)}"
    )

    # ---------------------------------------------------------
    # 2. Get metadata for each candidate repository
    # ---------------------------------------------------------
    repositories = []

    for github_url in candidate_urls:

        try:
            repository = (
                await github_client.get_repository_metadata(
                    github_url
                )
            )
            repository["source"] = "explicit_paper_source"
            repositories.append(repository)

        except Exception as exc:
            print(
                f"Skipping repository "
                f"{github_url}: {exc}"
            )

    # ---------------------------------------------------------
    # 3. Deterministically select the best repository
    # ---------------------------------------------------------
    best = matcher.select_best_repository(
        paper,
        repositories
    )

    github_url = None
    github_stars = None
    match_confidence = 0.0
    match_evidence = []

    if best is not None:

        repository = best["repository"]

        github_url = (
            repository.get("html_url")
            or repository.get("url")
        )

        github_stars = repository.get(
            "stargazers_count"
        )

        match_confidence = (
            best["score"] / 100.0
        )

        match_evidence = best["evidence"]

    # ---------------------------------------------------------
    # 4. Build canonical research-paper record
    # ---------------------------------------------------------
    record = build_research_paper_record(
        {
            **paper,
            "github_url": github_url,
            "github_stars": github_stars,
        }
    )

    # Internal metadata useful for auditing.
    record["content"]["repository_match"] = {
        "confidence": match_confidence,
        "evidence": match_evidence,
        "candidate_count": len(repositories),
    }

    return record


async def main():

    crawler = AsyncCrawler(
        max_concurrency=5
    )

    await crawler.start()

    try:

        # -----------------------------------------------------
        # 5. Get one REAL paper from arXiv
        # -----------------------------------------------------
        arxiv_client = ArxivClient(crawler)

        papers = await arxiv_client.search(
            query="id:2605.12975",
            start=0,
            max_results=1,
        )

        if not papers:
            raise RuntimeError(
                "Could not retrieve test paper."
            )

        paper = papers[0]

        print("\n=== SOURCE PAPER ===")

        print(
            f"Title: {paper['title']}"
        )

        print(
            f"URL: {paper['paper_url']}"
        )

        # -----------------------------------------------------
        # 6. Run enrichment
        # -----------------------------------------------------
        record = await enrich_paper(
            crawler,
            paper
        )

        print("\n=== ENRICHED RECORD ===")

        print(
            json.dumps(
                record,
                indent=2,
                ensure_ascii=False,
            )
        )

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
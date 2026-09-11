import asyncio
import json

from src.crawler.base import AsyncCrawler
from src.extraction.record import build_research_paper_record
from src.github.client import GitHubClient
from src.research.arxiv import ArxivClient
from src.research.paperswithcode import PapersWithCodeClient
from src.research.repository_matcher import RepositoryMatcher


async def enrich_paper(crawler, paper):
    """
    Enrich one arXiv paper with a verified GitHub repository
    and its current GitHub star count.
    """

    pwc_client = PapersWithCodeClient(crawler)
    github_client = GitHubClient(crawler)
    matcher = RepositoryMatcher()

    # ---------------------------------------------------------
    # 1. Extract the arXiv ID
    # ---------------------------------------------------------
    arxiv_id = matcher.extract_arxiv_id(
        paper["paper_url"]
    )

    if not arxiv_id:
        raise ValueError(
            f"Could not extract arXiv ID from "
            f"{paper['paper_url']}"
        )

    # ---------------------------------------------------------
    # 2. Discover candidate repositories
    # ---------------------------------------------------------
    pwc_result = await pwc_client.get_paper(
        arxiv_id
    )

    candidate_urls = pwc_result["github_urls"]

    print("\n=== GITHUB CANDIDATES ===")

    for url in candidate_urls:
        print(url)

    print(
        f"\nTotal candidates: {len(candidate_urls)}"
    )

    repositories = []

    # ---------------------------------------------------------
    # 3. Get metadata for each candidate repository
    # ---------------------------------------------------------
    for github_url in candidate_urls:

        try:
            repository = (
                await github_client.get_repository_metadata(
                    github_url
                )
            )

            repositories.append(repository)

        except Exception as exc:
            print(
                f"Skipping repository "
                f"{github_url}: {exc}"
            )

    # ---------------------------------------------------------
    # 4. Deterministically select best repository
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

        github_url = repository.get(
            "html_url"
        ) or repository.get(
            "url"
        )

        github_stars = repository.get(
            "stargazers_count"
        )

        match_confidence = (
            best["score"] / 100.0
        )

        match_evidence = best["evidence"]

    # ---------------------------------------------------------
    # 5. Build canonical research-paper record
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
        # 6. Get one REAL paper from arXiv
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
        # 7. Run enrichment
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
import asyncio
import json

from src.crawler.base import AsyncCrawler
from src.github.client import GitHubClient
from src.research.arxiv import ArxivClient
from src.research.paperswithcode import PapersWithCodeClient
from src.research.repository_matcher import RepositoryMatcher
from src.extraction.record import build_research_paper_record


async def enrich_paper(
    crawler,
    paper
):

    pwc = PapersWithCodeClient(crawler)
    github = GitHubClient(crawler)
    matcher = RepositoryMatcher()

    arxiv_id = matcher.extract_arxiv_id(
        paper["paper_url"]
    )

    pwc_result = await pwc.get_paper(
        arxiv_id
    )

    repositories = []

    for github_url in pwc_result["github_urls"]:

        try:

            repository = await github.get_repository_metadata(
                github_url
            )

            repositories.append(
                repository
            )

        except Exception:

            continue

    best = matcher.select_best_repository(
        paper,
        repositories
    )

    github_url = None
    github_stars = None
    confidence = 0.0
    evidence = None

    if best:

        repository = best["repository"]

        github_url = repository["html_url"]
        github_stars = repository["stargazers_count"]
        confidence = best["score"] / 100
        evidence = best["evidence"]

    record = build_research_paper_record(
        {
            **paper,
            "github_url": github_url,
            "github_stars": github_stars,
        }
    )

    record["content"]["repository_match"] = {
        "confidence": confidence,
        "evidence": evidence,
        "candidate_count": len(repositories),
    }

    return record


async def main():

    crawler = AsyncCrawler(
        max_concurrency=5
    )

    await crawler.start()

    try:

        arxiv = ArxivClient(crawler)

        papers = await arxiv.search(
            query="id:2605.12975",
            start=0,
            max_results=1,
        )

        if not papers:
            print("Paper not found.")
            return

        paper = papers[0]

        print("\n=== SOURCE PAPER ===")
        print(paper["title"])
        print(paper["paper_url"])

        enriched = await enrich_paper(
            crawler,
            paper
        )

        print("\n=== ENRICHED RECORD ===")
        print(
            json.dumps(
                enriched,
                indent=2,
                ensure_ascii=False,
            )
        )

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
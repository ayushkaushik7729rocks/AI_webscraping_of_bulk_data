import asyncio
import json

from src.crawler.base import AsyncCrawler
from src.extraction.record import build_research_paper_record
from src.github.client import GitHubClient
from src.research.arxiv import ArxivClient
from src.research.repository_matcher import RepositoryMatcher
from src.research.paperswithcode import PapersWithCodeClient

# async def enrich_paper(crawler, paper):
#     """
#     Enrich one arXiv paper with a verified GitHub repository
#     and its current GitHub star count.
#     """

#     arxiv_client = ArxivClient(crawler)
#     github_client = GitHubClient(crawler)
#     matcher = RepositoryMatcher()

#     # ---------------------------------------------------------
#     # 1. Discover GitHub repositories from the arXiv paper page
#     # ---------------------------------------------------------

#     candidate_urls = await arxiv_client.get_github_urls(
#         paper["paper_url"]
#     )

#     repositories = []

#     # ---------------------------------------------------------
#     # 2. Get metadata for each candidate repository
#     # ---------------------------------------------------------

#     for github_url in candidate_urls:

#         try:

#             repository = (
#                 await github_client.get_repository_metadata(
#                     github_url
#                 )
#             )

#             repository["source"] = "explicit_paper_source"

#             repositories.append(repository)

#         except Exception as exc:

#             print(
#                 f"Skipping repository "
#                 f"{github_url}: {exc}"
#             )

#     # ---------------------------------------------------------
#     # 3. Deterministically select the best repository
#     # ---------------------------------------------------------

#     best = matcher.select_best_repository(
#         paper,
#         repositories
#     )

#     github_url = None
#     github_stars = None
#     match_confidence = 0.0
#     match_evidence = []

#     if best is not None:

#         repository = best["repository"]

#         github_url = (
#             repository.get("html_url")
#             or repository.get("url")
#         )

#         github_stars = repository.get(
#             "stargazers_count"
#         )

#         match_confidence = (
#             best["score"] / 100.0
#         )

#         match_evidence = best["evidence"]

#     # ---------------------------------------------------------
#     # 4. Build canonical research-paper record
#     # ---------------------------------------------------------

#     record = build_research_paper_record(
#         {
#             **paper,
#             "github_url": github_url,
#             "github_stars": github_stars,
#         }
#     )

#     record["content"]["repository_match"] = {
#         "confidence": match_confidence,
#         "evidence": match_evidence,
#         "candidate_count": len(repositories),
#     }

#     return record
async def enrich_paper(crawler, paper):
    """
    Enrich one arXiv paper with a verified GitHub repository
    and its current GitHub star count.

    Repository discovery order:
        1. arXiv paper page
        2. Papers With Code fallback
    """

    arxiv_client = ArxivClient(crawler)
    github_client = GitHubClient(crawler)
    pwc_client = PapersWithCodeClient(crawler)
    matcher = RepositoryMatcher()

    # ---------------------------------------------------------
    # 1. Discover GitHub repositories from the arXiv paper page
    # ---------------------------------------------------------

    candidate_urls = await arxiv_client.get_github_urls(
        paper["paper_url"]
    )

    repository_source = "explicit_paper_source"

    # ---------------------------------------------------------
    # 2. Papers With Code fallback
    # ---------------------------------------------------------

    if not candidate_urls:

        arxiv_id = matcher.extract_arxiv_id(
            paper["paper_url"]
        )

        if arxiv_id:

            try:

                pwc_result = await pwc_client.get_paper(
                    arxiv_id
                )

                candidate_urls = pwc_result.get(
                    "github_urls",
                    []
                )

                if candidate_urls:
                    repository_source = (
                        "paperswithcode_source"
                    )

            except Exception as exc:

                print(
                    f"Papers With Code lookup failed "
                    f"for {arxiv_id}: {exc}"
                )

    # ---------------------------------------------------------
    # 3. Get metadata for each candidate repository
    # ---------------------------------------------------------

    repositories = []

    for github_url in candidate_urls:

        try:

            repository = (
                await github_client.get_repository_metadata(
                    github_url
                )
            )

            repository["source"] = repository_source

            repositories.append(repository)

        except Exception as exc:

            print(
                f"Skipping repository "
                f"{github_url}: {exc}"
            )

    # ---------------------------------------------------------
    # 4. Deterministically select the best repository
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
    # 5. Build canonical research-paper record
    # ---------------------------------------------------------

    record = build_research_paper_record(
        {
            **paper,
            "github_url": github_url,
            "github_stars": github_stars,
        }
    )

    record["content"]["repository_match"] = {
        "confidence": match_confidence,
        "evidence": match_evidence,
        "candidate_count": len(repositories),
        "discovery_source": repository_source
            if repositories
            else None,
    }

    return record


async def enrich_paper_with_limit(
    crawler,
    paper,
    semaphore,
    index
):
    """
    Enrich one paper while respecting the global
    paper-enrichment concurrency limit.
    """

    async with semaphore:

        print(
            f"[START] Paper {index}: "
            f"{paper['title']}"
        )

        try:

            record = await enrich_paper(
                crawler,
                paper
            )

            print(
                f"[DONE] Paper {index}: "
                f"{record['content']['title']}"
            )

            return record

        except Exception as exc:

            print(
                f"[ERROR] Paper {index}: "
                f"{exc}"
            )

            return None


async def enrich_papers(
    crawler,
    papers,
    max_concurrency=5
):
    """
    Enrich multiple papers concurrently.

    max_concurrency limits how many paper enrichment
    tasks can run simultaneously.
    """

    semaphore = asyncio.Semaphore(
        max_concurrency
    )

    tasks = [
        enrich_paper_with_limit(
            crawler,
            paper,
            semaphore,
            index
        )
        for index, paper in enumerate(
            papers,
            start=1
        )
    ]

    results = await asyncio.gather(
        *tasks
    )

    # Remove failed records while preserving
    # the original paper ordering.
    return [
        record
        for record in results
        if record is not None
    ]


async def main():

    crawler = AsyncCrawler(
        max_concurrency=5
    )

    await crawler.start()

    try:

        # -----------------------------------------------------
        # Test with multiple REAL arXiv papers
        # -----------------------------------------------------

        arxiv_client = ArxivClient(
            crawler
        )

        papers = await arxiv_client.search(
            query="cat:cs.AI",
            start=0,
            max_results=5,
        )

        if not papers:

            raise RuntimeError(
                "Could not retrieve papers."
            )

        print(
            f"\nRetrieved {len(papers)} papers."
        )

        # -----------------------------------------------------
        # Concurrent enrichment
        # -----------------------------------------------------

        records = await enrich_papers(
            crawler,
            papers,
            max_concurrency=5
        )

        print(
            f"\nSuccessfully enriched "
            f"{len(records)}/{len(papers)} papers."
        )

        # -----------------------------------------------------
        # Display results
        # -----------------------------------------------------

        for record in records:

            content = record["content"]

            print("\n----------------------------------------")

            print(
                f"Title: {content['title']}"
            )

            print(
                f"GitHub: {content['github_url']}"
            )

            print(
                f"Stars: {content['github_stars']}"
            )

            print(
                "Match confidence: "
                f"{content['repository_match']['confidence']}"
            )

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler
from src.research.run_enrichment import enrich_papers


INPUT_FILE = Path("data/research_papers_100.json")
OUTPUT_FILE = Path("data/research_papers_100_enriched.json")


async def main():

    # ---------------------------------------------------------
    # 1. Load the 100 papers collected from ArXiv
    # ---------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    print(
        f"\nLoaded {len(records)} papers."
    )

    if not records:
        raise RuntimeError(
            "No papers found in input file."
        )

    # ---------------------------------------------------------
    # 2. Convert canonical records into the format expected
    #    by enrich_papers()
    # ---------------------------------------------------------

    papers = []

    for record in records:

        content = record["content"]

        papers.append({
            "title": content["title"],
            "authors": content["authors"],
            "paper_url": content["paper_url"],
            "published_date": content["published_date"],
            "github_url": content.get("github_url"),
            "github_stars": content.get("github_stars"),
            "links": [],
        })

    # ---------------------------------------------------------
    # 3. Start crawler
    # ---------------------------------------------------------

    crawler = AsyncCrawler(
        max_concurrency=5
    )

    await crawler.start()

    try:

        # -----------------------------------------------------
        # 4. Run the EXISTING enrichment pipeline
        # -----------------------------------------------------

        enriched_records = await enrich_papers(
            crawler=crawler,
            papers=papers,
            max_concurrency=5
        )

    finally:

        await crawler.close()

    # ---------------------------------------------------------
    # 5. Save enriched records
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            enriched_records,
            file,
            indent=2,
            ensure_ascii=False
        )

    # ---------------------------------------------------------
    # 6. Calculate enrichment statistics
    # ---------------------------------------------------------

    github_found = 0
    github_missing = 0
    stars_found = 0

    for record in enriched_records:

        content = record["content"]

        if content.get("github_url"):
            github_found += 1
        else:
            github_missing += 1

        if content.get("github_stars") is not None:
            stars_found += 1

    # ---------------------------------------------------------
    # 7. Print summary
    # ---------------------------------------------------------

    print("\n========================================")
    print("GITHUB ENRICHMENT SUMMARY")
    print("========================================")

    print(
        "Input papers:",
        len(papers)
    )

    print(
        "Successfully enriched:",
        len(enriched_records)
    )

    print(
        "GitHub repositories found:",
        github_found
    )

    print(
        "No GitHub repository found:",
        github_missing
    )

    print(
        "GitHub star counts found:",
        stars_found
    )

    print(
        "\nSaved enriched dataset to:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    asyncio.run(main())
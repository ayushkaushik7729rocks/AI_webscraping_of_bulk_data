import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler
from src.startups.startuphub import StartupHubSource
from src.startups.paginator import StartupHubPaginator
from src.startups.relevance import StartupRelevanceFilter
from src.startups.checkpoint import StartupCheckpoint
from src.startups.run_startups_1000 import StartupCollector


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:
        paginator = StartupHubPaginator(
            source=StartupHubSource,
            crawler=crawler,
            delay_seconds=2,
        )

        relevance_filter = StartupRelevanceFilter()

        checkpoint = StartupCheckpoint(
            "data/startup_checkpoint.json"
        )

        collector = StartupCollector(
            paginator=paginator,
            relevance_filter=relevance_filter,
            checkpoint=checkpoint,
            target_count=10,
        )

        result = await collector.collect()

        accepted = result["accepted"]
        review = result["review"]

        print("\n" + "=" * 70)
        print("STARTUP LIVE INTEGRATION RESULT")
        print("=" * 70)

        print("Accepted:", len(accepted))
        print("Review:", len(review))

        print("\nAccepted startups:")

        for startup in accepted:
            print(
                startup["name"],
                "→",
                startup["source_url"]
            )

        print("\nReview startups:", len(review))

        output_path = Path(
            "data/startups_live_test.json"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        print("\nSaved:", output_path)

        print("=" * 70)

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
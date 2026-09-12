import asyncio
import json
from pathlib import Path
from src.crawler.base import AsyncCrawler
from src.startups.startuphub import StartupHubSource
from src.startups.paginator import StartupHubPaginator


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

        startups = await paginator.fetch_pages(
            max_pages=3
        )

        print("\n" + "=" * 70)
        print("LIVE PAGINATION RESULT")
        print("=" * 70)

        print(
            "Total extracted:",
            len(startups)
        )

        unique_urls = {
            startup["source_url"]
            for startup in startups
        }

        print(
            "Unique URLs:",
            len(unique_urls)
        )

        # Save collected startups to JSON
        output_path = Path(
            "data/startuphub_300.json"
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
                startups,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(
            "Saved:",
            output_path
        )

        print("\nFirst 20 startups:")

        for startup in startups[:20]:
            print(
                startup["name"],
                "→",
                startup["source_url"]
            )

        print("\n" + "=" * 70)

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())


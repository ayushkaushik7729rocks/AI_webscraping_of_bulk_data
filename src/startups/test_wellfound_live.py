import asyncio

from src.crawler.base import AsyncCrawler
from src.startups.wellfound import WellfoundStartupSource
from src.startups.extractor import StartupExtractor
from src.startups.dedup import StartupDeduplicator


async def main():

    url = WellfoundStartupSource.page_url(1)

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        result = await crawler.fetch(url)

    finally:

        await crawler.close()

    print("HTTP status:", result["status"])

    if result["status"] != 200:
        print("ERROR:", result["error"])
        return

    startups = (
        WellfoundStartupSource.extract_startups(
            result["html"],
            url
        )
    )

    valid_startups = []

    for startup in startups:

        startup = StartupExtractor.clean(
            startup
        )

        if StartupExtractor.validate(
            startup
        ):
            valid_startups.append(
                startup
            )

    unique_startups = (
        StartupDeduplicator.deduplicate(
            valid_startups
        )
    )

    print(
        "Extracted startups:",
        len(startups)
    )

    print(
        "Valid startups:",
        len(valid_startups)
    )

    print(
        "Unique startups:",
        len(unique_startups)
    )

    print("\nFirst 10 records:")

    for startup in unique_startups[:10]:

        print(
            startup["name"],
            "→",
            startup["source_url"]
        )


if __name__ == "__main__":
    asyncio.run(main())
import asyncio

from src.crawler.base import AsyncCrawler
from src.research.arxiv import ArxivClient


async def main():

    crawler = AsyncCrawler(max_concurrency=1)
    await crawler.start()

    try:

        client = ArxivClient(crawler)

        urls = await client.get_github_urls(
            "http://arxiv.org/abs/2605.12975v1"
        )

        print("=== ARXIV GITHUB URLS ===")

        for url in urls:
            print(url)

        print(f"\nTotal: {len(urls)}")

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
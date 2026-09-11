import asyncio

from src.crawler.base import AsyncCrawler
from src.github.client import GitHubClient


async def main():
    crawler = AsyncCrawler(max_concurrency=1)
    await crawler.start()

    try:
        client = GitHubClient(crawler)

        result = await client.get_repository_metadata(
            "https://github.com/GasolSun36/PyRAG"
        )

        print("=== GITHUB TEST ===")
        print(f"Repository: {result['full_name']}")
        print(f"Stars: {result['stargazers_count']}")
        print(f"URL: {result['html_url']}")

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
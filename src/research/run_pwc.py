import asyncio

from src.crawler.base import AsyncCrawler
from src.research.paperswithcode import PapersWithCodeClient


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    pwc = PapersWithCodeClient(crawler)

    result = await pwc.get_paper(
        "98456"
    )

    print("Papers with Code URL:")
    print(result["url"])

    print("\nGitHub URLs:")
    for url in result["github_urls"]:
        print(url)

    print("\nError:")
    print(result["error"])

    await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
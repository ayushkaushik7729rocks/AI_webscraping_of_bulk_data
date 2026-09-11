import asyncio

from src.crawler.base import AsyncCrawler
from src.github.client import GitHubClient


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    github = GitHubClient(crawler)

    repository = await github.get_repository(
        "openai",
        "openai-python"
    )

    print("Repository:", repository["full_name"])
    print("URL:", repository["html_url"])
    print("Description:", repository["description"])
    print("Stars:", repository["stargazers_count"])

    stars = await github.get_star_count(
        "openai",
        "openai-python"
    )

    print("Stars through client:", stars)

    await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
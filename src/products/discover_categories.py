import asyncio
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.crawler.base import AsyncCrawler


BASE_URL = "https://www.futurepedia.io/ai-tools"


def extract_categories(html):

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    categories = set()

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link["href"]

        parsed = urlparse(href)

        if parsed.netloc not in {
            "",
            "www.futurepedia.io"
        }:
            continue

        path = parsed.path.rstrip("/")

        prefix = "/ai-tools/"

        if not path.startswith(prefix):
            continue

        category = path[len(prefix):]

        if not category:
            continue

        if "/" in category:
            continue

        categories.add(category)

    return sorted(categories)


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        result = await crawler.fetch(
            BASE_URL
        )

        print(
            "HTTP status:",
            result["status"]
        )

        if result["status"] != 200:
            raise RuntimeError(
                f"Failed: HTTP {result['status']}"
            )

        categories = extract_categories(
            result["html"]
        )

        print(
            "\nCategories found:",
            len(categories)
        )

        for category in categories:
            print(category)

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
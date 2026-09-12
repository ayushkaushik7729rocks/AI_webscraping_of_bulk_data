import asyncio

from bs4 import BeautifulSoup

from src.crawler.base import AsyncCrawler
from src.products.producthunt import ProductHuntProductSource


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        url = ProductHuntProductSource.page_url(1)

        result = await crawler.fetch(url)

        if result["status"] != 200:
            print("HTTP:", result["status"])
            return

        soup = BeautifulSoup(
            result["html"],
            "lxml"
        )

        # Find the actual Wordware product link.
        link = soup.find(
            "a",
            href="/products/wordware"
        )

        if not link:
            print("Wordware link not found")
            return

        print("=" * 80)
        print("WORDWARE LINK")
        print("=" * 80)

        print(link.prettify())

        print("\n" + "=" * 80)
        print("PARENT")
        print("=" * 80)

        parent = link.parent

        if parent:
            print(parent.prettify())

        print("\n" + "=" * 80)
        print("GRANDPARENT")
        print("=" * 80)

        if parent and parent.parent:
            print(parent.parent.prettify())

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
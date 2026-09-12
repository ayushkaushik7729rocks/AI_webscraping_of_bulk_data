import asyncio
from bs4 import BeautifulSoup

from src.crawler.base import AsyncCrawler


URL = (
    "https://www.producthunt.com/products"
    "?parentTopic=development"
    "&period=all-time"
    "&topic=artificial-intelligence"
)


async def main():

    crawler = AsyncCrawler(max_concurrency=1)
    await crawler.start()

    try:
        result = await crawler.fetch(URL)

        print("Status:", result["status"])
        print("Final URL:", result["url"])
        print("HTML length:", len(result["html"] or ""))

        if result["status"] != 200:
            print("ERROR:", result["error"])
            return

        soup = BeautifulSoup(
            result["html"],
            "lxml"
        )

        print("\nTITLE:")
        print(
            soup.title.get_text(strip=True)
            if soup.title
            else None
        )

        print("\nPRODUCT-LIKE LINKS:")

        count = 0

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if "/products/" not in href:
                continue

            text = link.get_text(
                " ",
                strip=True
            )

            if not text:
                continue

            print(
                repr(text[:100]),
                "->",
                href
            )

            count += 1

            if count >= 30:
                break

        print(
            "\nMatching links shown:",
            count
        )

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
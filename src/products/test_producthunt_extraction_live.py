import asyncio

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

        print("Status:", result["status"])
        print("URL:", result["url"])
        print("HTML length:", len(result["html"] or ""))

        if result["status"] != 200:
            print("Error:", result["error"])
            return

        products = (
            ProductHuntProductSource.extract_products(
                result["html"],
                result["url"]
            )
        )

        print(
            "\nProducts extracted:",
            len(products)
        )

        for index, product in enumerate(
            products,
            start=1
        ):
            print(
                f"{index}. "
                f"{product['name']} | "
                f"{product['source_url']}"
            )

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
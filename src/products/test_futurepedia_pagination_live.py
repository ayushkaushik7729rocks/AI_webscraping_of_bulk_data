import asyncio

from src.crawler.base import AsyncCrawler
from src.products.futurepedia import FuturepediaProductSource
from src.products.paginator import FuturepediaPaginator


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        paginator = FuturepediaPaginator(
            source=FuturepediaProductSource,
            crawler=crawler,
            category="ai-agents",
            delay_seconds=2
        )

        all_urls = set()

        for page in range(1, 4):

            print("\n" + "=" * 70)
            print(f"PAGE {page}")
            print("=" * 70)

            products = await paginator.fetch_page(page)

            print(
                "Products extracted:",
                len(products)
            )

            page_urls = {
                product["source_url"]
                for product in products
            }

            new_urls = page_urls - all_urls

            print(
                "Unique products on this page:",
                len(page_urls)
            )

            print(
                "New products:",
                len(new_urls)
            )

            all_urls.update(page_urls)

            for product in products[:5]:
                print(
                    product["name"],
                    "| Rating:",
                    product["rating"],
                    "|",
                    product["source_url"]
                )

        print("\n" + "=" * 70)
        print("PAGINATION SUMMARY")
        print("=" * 70)

        print(
            "Total unique products:",
            len(all_urls)
        )

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
import asyncio

from src.crawler.base import AsyncCrawler
from src.products.futurepedia import FuturepediaProductSource


CATEGORIES = [
    "ai-agents",
    "art",
    "audio-generators",
    "image-generators",
    "productivity",
    "text-generators",
    "video",
]


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        global_urls = set()

        for category in CATEGORIES:

            print("\n" + "=" * 70)
            print("CATEGORY:", category)
            print("=" * 70)

            category_urls = set()

            for page in range(1, 11):

                url = FuturepediaProductSource.page_url(
                    page=page,
                    category=category
                )

                result = await crawler.fetch(url)

                if result["status"] != 200:
                    print(
                        f"Page {page}: HTTP {result['status']}"
                    )
                    break

                products = (
                    FuturepediaProductSource.extract_products(
                        result["html"],
                        result["url"]
                    )
                )

                new_products = []

                for product in products:

                    product_url = product["source_url"]

                    if product_url in category_urls:
                        continue

                    category_urls.add(product_url)
                    new_products.append(product)

                global_new = 0

                for product in new_products:

                    product_url = product["source_url"]

                    if product_url not in global_urls:
                        global_urls.add(product_url)
                        global_new += 1

                print(
                    f"Page {page}: "
                    f"{len(products)} fetched, "
                    f"{len(new_products)} category-new, "
                    f"{global_new} globally-new, "
                    f"category total={len(category_urls)}, "
                    f"global total={len(global_urls)}"
                )

                # Stop if this page contains no new products.
                if not new_products:
                    print(
                        "Category exhausted "
                        "(no new products on this page)."
                    )
                    break

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
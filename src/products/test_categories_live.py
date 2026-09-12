# import asyncio

# from src.crawler.base import AsyncCrawler
# from src.products.futurepedia import FuturepediaProductSource


# CATEGORIES = [
#     "ai-agents",
#     "productivity",
#     "code",
#     "research-assistant",
#     "technology-and-it",
#     "operations",
#     "business",
# ]


# async def main():

#     crawler = AsyncCrawler(
#         max_concurrency=1
#     )

#     await crawler.start()

#     try:

#         for category in CATEGORIES:

#             url = FuturepediaProductSource.page_url(
#                 page=1,
#                 category=category
#             )

#             print("\n" + "=" * 70)
#             print("CATEGORY:", category)
#             print("URL:", url)
#             print("=" * 70)

#             result = await crawler.fetch(url)

#             print(
#                 "HTTP status:",
#                 result["status"]
#             )

#             if result["status"] != 200:
#                 print("FAILED")
#                 continue

#             products = (
#                 FuturepediaProductSource.extract_products(
#                     result["html"],
#                     result["url"]
#                 )
#             )

#             unique_urls = {
#                 product["source_url"]
#                 for product in products
#             }

#             print(
#                 "Products extracted:",
#                 len(products)
#             )

#             print(
#                 "Unique URLs:",
#                 len(unique_urls)
#             )

#     finally:

#         await crawler.close()


# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio

from src.crawler.base import AsyncCrawler
from src.products.futurepedia import FuturepediaProductSource


CATEGORIES = [
    "ai-agents",
    "productivity",
    "code",
    "research-assistant",
    "technology-and-it",
    "operations",
    "business",
]


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        for category in CATEGORIES:

            print("\n" + "=" * 70)
            print("CATEGORY:", category)
            print("=" * 70)

            category_urls = set()

            for page in range(1, 6):

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

                new_products = [
                    product
                    for product in products
                    if product["source_url"] not in category_urls
                ]

                for product in new_products:
                    category_urls.add(
                        product["source_url"]
                    )

                print(
                    f"Page {page}: "
                    f"{len(products)} fetched, "
                    f"{len(new_products)} new, "
                    f"category total={len(category_urls)}"
                )

                if not products:
                    print(
                        "Category appears exhausted."
                    )
                    break

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
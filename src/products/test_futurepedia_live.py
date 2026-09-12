# import asyncio

# from src.crawler.base import AsyncCrawler
# from src.products.futurepedia import FuturepediaProductSource


# # async def main():

# #     crawler = AsyncCrawler(
# #         max_concurrency=1
# #     )

# #     await crawler.start()

# #     try:

# #         url = FuturepediaProductSource.page_url(
# #             1,
# #             category="ai-agents"
# #         )

# #         result = await crawler.fetch(
# #             url
# #         )

# #         print("=" * 70)
# #         print("FUTUREPEDIA PRODUCT EXTRACTION TEST")
# #         print("=" * 70)

# #         print("Status:", result["status"])
# #         print("URL:", result["url"])

# #         products = (
# #             FuturepediaProductSource.inspect_product(
# #                 result["html"]
# #             )
# #         )

# #         print(
# #             "Products extracted:",
# #             len(products)
# #         )

# #         print("\nProducts:")

# #         for product in products:
# #             print(
# #                 product["name"],
# #                 "| Rating:",
# #                 product["rating"],
# #                 "|",
# #                 product["source_url"]
# #             )

# #     finally:
# #         await crawler.close()
# async def main():

#     crawler = AsyncCrawler(
#         max_concurrency=1
#     )

#     await crawler.start()

#     try:

#         url = FuturepediaProductSource.page_url(
#             1,
#             category="ai-agents"
#         )

#         result = await crawler.fetch(
#             url
#         )

#         print("=" * 70)
#         print("FUTUREPEDIA PRODUCT CARD INSPECTION")
#         print("=" * 70)

#         print("Status:", result["status"])
#         print("URL:", result["url"])
#         # print(
#         #     "HTML length:",
#         #     len(result["html"])
#         # )

#         if result["status"] == 200:

#             FuturepediaProductSource.inspect_product(
#                 result["html"],
                
#             )

#     finally:
#         await crawler.close()

# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio

from src.crawler.base import AsyncCrawler
from src.products.futurepedia import FuturepediaProductSource


async def main():

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:

        url = FuturepediaProductSource.page_url(
            1,
            category="ai-agents"
        )

        result = await crawler.fetch(
            url
        )

        print("=" * 70)
        print("FUTUREPEDIA PRODUCT EXTRACTION TEST")
        print("=" * 70)

        print("Status:", result["status"])
        print("URL:", result["url"])
        print("HTML length:", len(result["html"]))

        if result["status"] != 200:
            print("Failed to fetch Futurepedia page.")
            return

        products = FuturepediaProductSource.extract_products(
            result["html"],
            result["url"]
        )

        print(
            "Products extracted:",
            len(products)
        )

        print("\nProducts:")

        for product in products:

            print(
                product["name"],
                "| Rating:",
                product["rating"],
                "|",
                product["source_url"]
            )

    finally:

        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
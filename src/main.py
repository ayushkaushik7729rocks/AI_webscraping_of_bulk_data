import asyncio
import time

from crawler.base import AsyncCrawler


async def main():

    crawler = AsyncCrawler(max_concurrency=3,max_retries=3)

    await crawler.start()

    urls = [
        "https://example.com",
        "https://example.org",
        "https://httpbin.org/get",
        "https://httpbin.org/status/404",
        "https://httpbin.org/delay/2",
    ]

    start_time = time.perf_counter()

    results = await crawler.fetch_many(urls)

    end_time = time.perf_counter()

    for result in results:

        print(
            "URL:",
            result["url"],
            "| Status:",
            result["status"],
            "| Error:",
            result["error"]
        )

    print("Time taken:", end_time - start_time, "seconds")

    await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
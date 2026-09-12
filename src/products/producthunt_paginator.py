import asyncio


class ProductHuntPaginator:

    def __init__(
        self,
        source,
        crawler,
        delay_seconds=2
    ):
        self.source = source
        self.crawler = crawler
        self.delay_seconds = delay_seconds

    async def fetch_page(self, page):
        if page > 1 and self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        url = self.source.page_url(page)

        result = await self.crawler.fetch(url)

        if result["status"] != 200:
            raise RuntimeError(
                f"Product Hunt page {page} failed: "
                f"status={result['status']}, "
                f"url={result['url']}"
            )

        products = self.source.extract_products(
            result["html"],
            result["url"]
        )

        return products
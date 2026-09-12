import asyncio


class FuturepediaPaginator:

    def __init__(
        self,
        source,
        crawler,
        category="ai-agents",
        delay_seconds=2
    ):
        self.source = source
        self.crawler = crawler
        self.category = category
        self.delay_seconds = delay_seconds

    async def fetch_page(self, page):

        if page > 1 and self.delay_seconds > 0:
            await asyncio.sleep(
                self.delay_seconds
            )

        url = self.source.page_url(
            page,
            category=self.category
        )

        result = await self.crawler.fetch(
            url
        )

        if result["status"] != 200:
            raise RuntimeError(
                f"Failed to fetch page {page}: "
                f"HTTP {result['status']}"
            )

        products = self.source.extract_products(
            result["html"],
            result["url"]
        )

        return products
import asyncio

from src.startups.dedup import StartupDeduplicator


class StartupHubPaginator:

    def __init__(
        self,
        source,
        crawler,
        delay_seconds=2,
    ):
        self.source = source
        self.crawler = crawler
        self.delay_seconds = delay_seconds

    async def fetch_page(self, page):
        url = self.source.page_url(page)

        result = await self.crawler.fetch(url)

        if result["status"] != 200:
            raise RuntimeError(
                f"Failed to fetch page {page}: "
                f"HTTP {result['status']} - "
                f"{result.get('error')}"
            )

        startups = self.source.extract_startups(
            result["html"],
            url
        )

        return startups

    async def fetch_pages(
        self,
        max_pages,
    ):
        all_startups = []

        for page in range(1, max_pages + 1):

            print(
                f"[START] StartupHub page {page}"
            )

            startups = await self.fetch_page(page)

            print(
                f"[DONE] Page {page}: "
                f"{len(startups)} startups"
            )

            all_startups.extend(startups)

            unique_startups = (
                StartupDeduplicator.deduplicate(
                    all_startups
                )
            )

            print(
                f"[TOTAL] Unique startups: "
                f"{len(unique_startups)}"
            )

            if page < max_pages:
                await asyncio.sleep(
                    self.delay_seconds
                )

        return StartupDeduplicator.deduplicate(
            all_startups
        )
import asyncio

from src.research.dedup import ResearchPaperDeduplicator


class ArxivPaginator:

    def __init__(
        self,
        client,
        page_size=100,
        delay_seconds=3
    ):
        self.client = client
        self.page_size = page_size
        self.delay_seconds = delay_seconds

    async def fetch_all(
        self,
        query,
        max_papers,
        start=0
    ):

        papers = []

        while len(
            ResearchPaperDeduplicator.deduplicate(papers)
        ) < max_papers:

            page = await self.client.search(
                query=query,
                start=start,
                max_results=self.page_size
            )

            if not page:
                break

            papers.extend(page)

            unique_papers = (
                ResearchPaperDeduplicator.deduplicate(
                    papers
                )
            )

            start += len(page)

            if len(page) < self.page_size:
                break

            if len(unique_papers) < max_papers:
                await asyncio.sleep(
                    self.delay_seconds
                )

        unique_papers = (
            ResearchPaperDeduplicator.deduplicate(
                papers
            )
        )

        return unique_papers[:max_papers]

    async def fetch_page(
        self,
        query,
        start=0
    ):
        """
        Fetch exactly one ArXiv page.

        Returns:
            {
                "papers": [...],
                "next_start": ...,
                "has_more": True/False
            }
        """

        page = await self.client.search(
            query=query,
            start=start,
            max_results=self.page_size
        )

        if not page:
            return {
                "papers": [],
                "next_start": start,
                "has_more": False
            }

        next_start = start + len(page)

        has_more = len(page) == self.page_size

        return {
            "papers": page,
            "next_start": next_start,
            "has_more": has_more
        }
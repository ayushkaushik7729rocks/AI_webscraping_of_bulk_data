import asyncio


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
        max_papers
    ):

        papers = []
        start = 0

        while len(papers) < max_papers:

            remaining = max_papers - len(papers)

            current_page_size = min(
                self.page_size,
                remaining
            )

            page = await self.client.search(
                query=query,
                start=start,
                max_results=current_page_size
            )

            if not page:
                break

            papers.extend(page)

            start += len(page)

            if len(page) < current_page_size:
                break

            if len(papers) < max_papers:
                await asyncio.sleep(
                    self.delay_seconds
                )

        return papers[:max_papers]
import pytest

from src.startups.paginator import StartupHubPaginator


class FakeSource:

    @staticmethod
    def page_url(page):
        return f"https://example.com/page/{page}"

    @staticmethod
    def extract_startups(html, source_url):
        return [
            {
                "name": html,
                "source_url": source_url,
                "source": "FakeSource",
            }
        ]


class FakeCrawler:

    def __init__(self):
        self.urls = []

    async def fetch(self, url):
        self.urls.append(url)

        return {
            "status": 200,
            "html": url,
            "error": None,
        }


@pytest.mark.asyncio
async def test_fetch_page():

    crawler = FakeCrawler()

    paginator = StartupHubPaginator(
        source=FakeSource,
        crawler=crawler,
        delay_seconds=0,
    )

    startups = await paginator.fetch_page(1)

    assert len(startups) == 1

    assert startups[0]["source_url"] == (
        "https://example.com/page/1"
    )


@pytest.mark.asyncio
async def test_fetch_pages():

    crawler = FakeCrawler()

    paginator = StartupHubPaginator(
        source=FakeSource,
        crawler=crawler,
        delay_seconds=0,
    )

    startups = await paginator.fetch_pages(
        max_pages=3
    )

    assert len(startups) == 3

    assert crawler.urls == [
        "https://example.com/page/1",
        "https://example.com/page/2",
        "https://example.com/page/3",
    ]


@pytest.mark.asyncio
async def test_fetch_page_handles_http_error():

    class ErrorCrawler:

        async def fetch(self, url):
            return {
                "status": 500,
                "html": "",
                "error": "server error",
            }

    paginator = StartupHubPaginator(
        source=FakeSource,
        crawler=ErrorCrawler(),
        delay_seconds=0,
    )

    with pytest.raises(RuntimeError):
        await paginator.fetch_page(1)
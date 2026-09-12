import pytest

from src.products.paginator import FuturepediaPaginator


class FakeSource:

    @staticmethod
    def page_url(page, category="ai-agents"):
        return f"https://example.com/{category}?page={page}"

    @staticmethod
    def extract_products(html, source_url):
        return [
            {
                "name": f"Product from {source_url}",
                "rating": 5.0,
                "source_url": source_url,
                "source": "Futurepedia",
                "category_url": source_url,
            }
        ]


class FakeCrawler:

    def __init__(self):
        self.requested_urls = []

    async def fetch(self, url):
        self.requested_urls.append(url)

        return {
            "status": 200,
            "url": url,
            "html": "<html></html>",
        }


@pytest.mark.asyncio
async def test_fetch_page():

    crawler = FakeCrawler()

    paginator = FuturepediaPaginator(
        source=FakeSource,
        crawler=crawler,
        category="ai-agents"
    )

    products = await paginator.fetch_page(2)

    assert len(products) == 1

    assert products[0]["name"] == (
        "Product from "
        "https://example.com/ai-agents?page=2"
    )

    assert crawler.requested_urls == [
        "https://example.com/ai-agents?page=2"
    ]


@pytest.mark.asyncio
async def test_fetch_page_failure():

    class FailingCrawler:

        async def fetch(self, url):
            return {
                "status": 500,
                "url": url,
                "html": "",
            }

    paginator = FuturepediaPaginator(
        source=FakeSource,
        crawler=FailingCrawler(),
        category="ai-agents"
    )

    with pytest.raises(RuntimeError):

        await paginator.fetch_page(1)
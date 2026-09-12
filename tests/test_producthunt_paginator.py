import pytest

from src.products.producthunt_paginator import ProductHuntPaginator


class FakeSource:

    @staticmethod
    def page_url(page):
        if page <= 1:
            return "https://example.com/products"

        return f"https://example.com/products?page={page}"

    @staticmethod
    def extract_products(html, source_url):
        return [
            {
                "name": html,
                "source_url": source_url
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
            "html": f"page-{len(self.requested_urls)}"
        }


@pytest.mark.asyncio
async def test_fetch_page():
    crawler = FakeCrawler()

    paginator = ProductHuntPaginator(
        source=FakeSource,
        crawler=crawler,
        delay_seconds=0
    )

    products = await paginator.fetch_page(1)

    assert len(products) == 1
    assert products[0]["name"] == "page-1"

    assert crawler.requested_urls == [
        "https://example.com/products"
    ]


@pytest.mark.asyncio
async def test_fetch_multiple_pages():
    crawler = FakeCrawler()

    paginator = ProductHuntPaginator(
        source=FakeSource,
        crawler=crawler,
        delay_seconds=0
    )

    page1 = await paginator.fetch_page(1)
    page2 = await paginator.fetch_page(2)

    assert page1[0]["name"] == "page-1"
    assert page2[0]["name"] == "page-2"

    assert crawler.requested_urls == [
        "https://example.com/products",
        "https://example.com/products?page=2"
    ]


@pytest.mark.asyncio
async def test_non_200_response_raises_error():
    class FailingCrawler:

        async def fetch(self, url):
            return {
                "status": 429,
                "url": url,
                "html": ""
            }

    paginator = ProductHuntPaginator(
        source=FakeSource,
        crawler=FailingCrawler(),
        delay_seconds=0
    )

    with pytest.raises(RuntimeError):
        await paginator.fetch_page(1)
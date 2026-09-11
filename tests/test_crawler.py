import pytest

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from src.crawler.base import AsyncCrawler


@pytest.mark.asyncio
async def test_fetch_example():

    crawler = AsyncCrawler()

    await crawler.start()

    result = await crawler.fetch("https://example.com")

    await crawler.close()

    assert result["status"] == 200
    assert result["error"] is None
    assert len(result["html"]) > 0


@pytest.mark.asyncio
async def test_429_retry():

    app = web.Application()

    request_count = 0

    async def rate_limit_handler(request):

        nonlocal request_count

        request_count += 1

        if request_count < 3:
            return web.Response(
                status=429,
                headers={"Retry-After": "0.1"}
            )

        return web.Response(
            status=200,
            text="<html>Success</html>"
        )

    app.router.add_get(
        "/rate-limit",
        rate_limit_handler
    )

    server = TestServer(app)
    await server.start_server()

    crawler = AsyncCrawler(
        max_concurrency=5,
        max_retries=3
    )

    await crawler.start()

    url = str(server.make_url("/rate-limit"))

    result = await crawler.fetch(url)

    await crawler.close()
    await server.close()

    assert result["status"] == 200
    assert result["error"] is None
    assert request_count == 3
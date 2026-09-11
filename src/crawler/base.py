import asyncio
import random

import aiohttp


class AsyncCrawler:

    def __init__(self, max_concurrency=5, max_retries=3):
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries

    async def start(self):
        timeout = aiohttp.ClientTimeout(total=10)

        self.session = aiohttp.ClientSession(
            timeout=timeout
        )

    async def close(self):
        if self.session:
            await self.session.close()

    async def fetch(self, url: str, headers=None):

        async with self.semaphore:

            for attempt in range(1, self.max_retries + 1):

                try:
                    async with self.session.get(url, headers=headers) as response:

                        # 429 = Too Many Requests
                        if response.status == 429:

                            if attempt == self.max_retries:
                                return {
                                    "url": url,
                                    "status": 429,
                                    "html": "",
                                    "error": "max retries exceeded",
                                }

                            retry_after = response.headers.get("Retry-After")

                            if retry_after:
                                try:
                                    delay = float(retry_after)
                                except ValueError:
                                    delay = 2 ** (attempt - 1)
                            else:
                                delay = 2 ** (attempt - 1)

                            jitter = random.uniform(0, 0.5)

                            print(
                                f"429 received for {url}. "
                                f"Retrying in {delay + jitter:.2f}s..."
                            )

                            await asyncio.sleep(delay + jitter)

                            continue

                        # Temporary server errors
                        if response.status in {500, 502, 503, 504}:

                            if attempt == self.max_retries:
                                return {
                                    "url": url,
                                    "status": response.status,
                                    "html": "",
                                    "error": "max retries exceeded",
                                }

                            delay = 2 ** (attempt - 1)
                            jitter = random.uniform(0, 0.5)

                            print(
                                f"{response.status} received for {url}. "
                                f"Retrying in {delay + jitter:.2f}s..."
                            )

                            await asyncio.sleep(delay + jitter)

                            continue

                        # Normal response
                        html = await response.text()

                        return {
                            "url": str(response.url),
                            "status": response.status,
                            "html": html,
                            "error": None,
                        }

                except asyncio.TimeoutError:

                    if attempt == self.max_retries:
                        return {
                            "url": url,
                            "status": None,
                            "html": "",
                            "error": "timeout - max retries exceeded",
                        }

                    delay = 2 ** (attempt - 1)
                    jitter = random.uniform(0, 0.5)

                    print(
                        f"Timeout for {url}. "
                        f"Retrying in {delay + jitter:.2f}s..."
                    )

                    await asyncio.sleep(delay + jitter)

                except aiohttp.ClientError as e:

                    if attempt == self.max_retries:
                        return {
                            "url": url,
                            "status": None,
                            "html": "",
                            "error": str(e),
                        }

                    delay = 2 ** (attempt - 1)
                    jitter = random.uniform(0, 0.5)

                    print(
                        f"Request error for {url}: {e}. "
                        f"Retrying in {delay + jitter:.2f}s..."
                    )

                    await asyncio.sleep(delay + jitter)

            return {
                "url": url,
                "status": None,
                "html": "",
                "error": "unknown error",
            }

    async def fetch_many(self, urls):

        tasks = []

        for url in urls:
            tasks.append(self.fetch(url))

        results = await asyncio.gather(*tasks)

        return results
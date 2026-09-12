import asyncio

from bs4 import BeautifulSoup

from src.crawler.base import AsyncCrawler
from src.startups.startuphub import StartupHubSource


async def main():

    url = StartupHubSource.page_url(1)

    print("Testing:", url)

    crawler = AsyncCrawler(
        max_concurrency=1
    )

    await crawler.start()

    try:
        result = await crawler.fetch(url)

    finally:
        await crawler.close()

    print("HTTP status:", result["status"])

    if result["status"] != 200:
        print("ERROR:", result["error"])
        return

    html = result["html"]

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    # ---------------------------------------------------------
    # Inspect specific startup HTML structures
    # ---------------------------------------------------------

    target_paths = [
        "/startups/01health",
        "/startups/09bbe",
        "/startups/0g-labs",
    ]

    for target_path in target_paths:

        target_link = soup.find(
            "a",
            href=target_path
        )

        if target_link:

            print("\n" + "=" * 70)
            print(f"{target_path} HTML STRUCTURE")
            print("=" * 70)

            print(
                target_link.prettify()[:5000]
            )

            print("=" * 70)

        else:

            print(
                f"\nCould not find {target_path}"
            )

    # ---------------------------------------------------------
    # Show total links
    # ---------------------------------------------------------

    links = soup.find_all(
        "a",
        href=True
    )

    print(
        "\nTotal links:",
        len(links)
    )

    # ---------------------------------------------------------
    # Show first 100 links
    # ---------------------------------------------------------

    print("\nFirst 100 links:")

    for link in links[:100]:

        text = link.get_text(
            " ",
            strip=True
        )

        href = link["href"].strip()

        print(
            repr(text[:80]),
            "→",
            href
        )

    # ---------------------------------------------------------
    # Test StartupHub extractor
    # ---------------------------------------------------------

    startups = (
        StartupHubSource.extract_startups(
            html,
            url
        )
    )

    print(
        "\nExtracted startup links:",
        len(startups)
    )

    # ---------------------------------------------------------
    # Show first 10 extracted startups
    # ---------------------------------------------------------

    print("\nFirst 10:")

    for startup in startups[:10]:

        print(
            startup["name"],
            "→",
            startup["source_url"]
        )


if __name__ == "__main__":
    asyncio.run(main())
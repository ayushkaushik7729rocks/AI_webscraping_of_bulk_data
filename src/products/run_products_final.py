import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler

from src.products.producthunt import ProductHuntProductSource
from src.products.producthunt_paginator import ProductHuntPaginator
from src.products.checkpoint import ProductCheckpoint


TARGET_COUNT = 1000

FUTUREPEDIA_FILE = Path(
    "data/products_1000.json"
)

PRODUCTHUNT_FILE = Path(
    "data/producthunt_products.json"
)

FINAL_FILE = Path(
    "data/products_1000.json"
)


def load_json_file(path):
    if not path.exists():
        return []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_json_file(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


async def collect_producthunt(
    crawler,
    existing_products
):

    checkpoint = ProductCheckpoint(
        "data/producthunt_checkpoint.json"
    )

    state = checkpoint.load()

    products = list(
        state.get("products", [])
    )

    seen_urls = set(
        state.get("seen_urls", [])
    )

    # Include products already collected
    # from Futurepedia so we don't duplicate them.
    for product in existing_products:

        url = product.get("source_url")

        if url:
            seen_urls.add(url)

    paginator = ProductHuntPaginator(
        source=ProductHuntProductSource,
        crawler=crawler,
        delay_seconds=2
    )

    last_completed_page = state.get(
        "last_completed_page",
        0
    )

    page = last_completed_page + 1

    while (
        len(existing_products) +
        len(products)
        < TARGET_COUNT
    ):

        print(
            f"\nFetching Product Hunt page {page}..."
        )

        page_products = (
            await paginator.fetch_page(page)
        )

        new_products = []

        for product in page_products:

            url = product.get(
                "source_url"
            )

            if not url:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            new_products.append(product)

        # Critical stopping condition.
        if not new_products:

            print(
                f"Page {page}: "
                f"{len(page_products)} fetched, "
                f"0 new."
            )

            print(
                "No new Product Hunt products. "
                "Stopping."
            )

            break

        products.extend(
            new_products
        )

        checkpoint.save(
            last_completed_page=page,
            products=products
        )

        total = (
            len(existing_products) +
            len(products)
        )

        print(
            f"Page {page}: "
            f"{len(page_products)} fetched, "
            f"{len(new_products)} new, "
            f"total={total}"
        )

        if total >= TARGET_COUNT:
            break

        page += 1

    return products


async def main():

    print("=" * 70)
    print("FRONTIER ATLAS — PRODUCT COLLECTION")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Load existing Futurepedia products
    # ---------------------------------------------------------

    futurepedia_products = []

    futurepedia_path = Path(
        "data/products_1000.json"
    )

    if futurepedia_path.exists():

        futurepedia_products = (
            load_json_file(
                futurepedia_path
            )
        )

        print(
            f"\nExisting Futurepedia products: "
            f"{len(futurepedia_products)}"
        )

    else:

        print(
            "\nNo existing Futurepedia output found."
        )

    # ---------------------------------------------------------
    # 2. Deduplicate Futurepedia
    # ---------------------------------------------------------

    unique_products = []
    seen_urls = set()

    for product in futurepedia_products:

        url = product.get(
            "source_url"
        )

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_products.append(product)

    print(
        f"Unique Futurepedia products: "
        f"{len(unique_products)}"
    )

    # ---------------------------------------------------------
    # 3. Check whether we already have 1000
    # ---------------------------------------------------------

    if len(unique_products) >= TARGET_COUNT:

        final_products = (
            unique_products[
                :TARGET_COUNT
            ]
        )

        save_json_file(
            FINAL_FILE,
            final_products
        )

        print(
            f"\nAlready have {TARGET_COUNT} "
            "unique products."
        )

        print(
            f"Saved: {FINAL_FILE}"
        )

        return

    # ---------------------------------------------------------
    # 4. Start crawler
    # ---------------------------------------------------------

    crawler = AsyncCrawler(
        max_concurrency=5,
        max_retries=3
    )

    await crawler.start()

    try:

        # -----------------------------------------------------
        # 5. Collect Product Hunt products
        # -----------------------------------------------------

        producthunt_products = (
            await collect_producthunt(
                crawler,
                unique_products
            )
        )

    finally:

        await crawler.close()

    # ---------------------------------------------------------
    # 6. Merge both sources
    # ---------------------------------------------------------

    all_products = []
    final_seen_urls = set()

    for product in (
        unique_products +
        producthunt_products
    ):

        url = product.get(
            "source_url"
        )

        if not url:
            continue

        if url in final_seen_urls:
            continue

        final_seen_urls.add(url)

        all_products.append(product)

        if len(all_products) >= TARGET_COUNT:
            break

    # ---------------------------------------------------------
    # 7. Save final output
    # ---------------------------------------------------------

    save_json_file(
        FINAL_FILE,
        all_products
    )

    print("\n" + "=" * 70)
    print("PRODUCT COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"Futurepedia unique: "
        f"{len(unique_products)}"
    )

    print(
        f"Product Hunt collected: "
        f"{len(producthunt_products)}"
    )

    print(
        f"Final unique products: "
        f"{len(all_products)}"
    )

    print(
        f"Saved to: {FINAL_FILE}"
    )

    # ---------------------------------------------------------
    # 8. Validation
    # ---------------------------------------------------------

    urls = [
        product["source_url"]
        for product in all_products
        if product.get("source_url")
    ]

    print(
        f"Unique URLs: {len(set(urls))}"
    )

    print(
        f"Missing URLs: "
        f"{sum(1 for p in all_products if not p.get('source_url'))}"
    )

    print(
        f"Missing names: "
        f"{sum(1 for p in all_products if not p.get('name'))}"
    )


if __name__ == "__main__":
    asyncio.run(main())
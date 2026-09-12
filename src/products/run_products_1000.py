import asyncio
import json
from pathlib import Path

from src.crawler.base import AsyncCrawler
from src.products.futurepedia import FuturepediaProductSource
from src.products.paginator import FuturepediaPaginator
from src.products.checkpoint import ProductCheckpoint
from src.products.collector import ProductCollector


TARGET_COUNT = 1000

CHECKPOINT_PATH = Path(
    "data/product_checkpoint.json"
)

OUTPUT_PATH = Path(
    "data/products_1000.json"
)


async def collect_products_1000():

    crawler = None

    try:
        crawler = AsyncCrawler(
            max_concurrency=1
        )

        await crawler.start()

        paginator = FuturepediaPaginator(
            source=FuturepediaProductSource,
            crawler=crawler,
            category="ai-agents",
            delay_seconds=2
        )

        checkpoint = ProductCheckpoint(
            CHECKPOINT_PATH
        )

        collector = ProductCollector(
            paginator=paginator,
            checkpoint=checkpoint,
            target_count=TARGET_COUNT
        )

        products = await collector.collect()

        OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                products,
                file,
                indent=2,
                ensure_ascii=False
            )

        print("\n" + "=" * 70)
        print("PRODUCT COLLECTION COMPLETE")
        print("=" * 70)

        print(
            "Products collected:",
            len(products)
        )

        print(
            "Output:",
            OUTPUT_PATH
        )

        print(
            "Checkpoint:",
            CHECKPOINT_PATH
        )

        print("=" * 70)

    finally:

        if crawler is not None:
            await crawler.close()


if __name__ == "__main__":
    asyncio.run(
        collect_products_1000()
    )
import asyncio
import json
from pathlib import Path

from src.startups.checkpoint import StartupCheckpoint


class StartupCollector:

    def __init__(
        self,
        paginator,
        relevance_filter,
        checkpoint,
        target_count=1000,
    ):
        self.paginator = paginator
        self.relevance_filter = relevance_filter
        self.checkpoint = checkpoint
        self.target_count = target_count

    async def collect(self):

        state = self.checkpoint.load()

        accepted = list(
            state.get("accepted", [])
        )

        review = list(
            state.get("review", [])
        )

        seen_urls = set(
            state.get("seen_urls", [])
        )

        last_completed_page = state.get(
            "last_completed_page",
            0
        )

        page = last_completed_page + 1

        while len(accepted) < self.target_count:

            print(
                f"\n[START] StartupHub page {page}"
            )

            startups = await self.paginator.fetch_page(
                page
            )

            print(
                f"[DONE] Page {page}: "
                f"{len(startups)} startups"
            )

            new_startups = []

            for startup in startups:

                source_url = startup.get(
                    "source_url"
                )

                if not source_url:
                    continue

                if source_url in seen_urls:
                    continue

                seen_urls.add(source_url)

                new_startups.append(startup)

            results = self.relevance_filter.filter(
                new_startups
            )

            accepted.extend(
                results["accepted"]
            )

            review.extend(
                results["review"]
            )

            rejected_count = len(
                results["rejected"]
            )

            print(
                f"[PAGE RESULT] "
                f"Accepted: {len(results['accepted'])}, "
                f"Review: {len(results['review'])}, "
                f"Rejected: {rejected_count}"
            )

            self.checkpoint.save(
                last_completed_page=page,
                accepted=accepted,
                review=review,
            )

            print(
                f"[TOTAL] Accepted: "
                f"{len(accepted)}/{self.target_count}"
            )

            if len(accepted) >= self.target_count:
                break

            page += 1

        accepted = accepted[
            :self.target_count
        ]

        return {
            "accepted": accepted,
            "review": review,
        }


TARGET_COUNT = 1000

CHECKPOINT_PATH = Path(
    "data/startup_checkpoint.json"
)

OUTPUT_PATH = Path(
    "data/startups_1000.json"
)

REVIEW_OUTPUT_PATH = Path(
    "data/startups_review.json"
)


async def collect_startups_1000():

    crawler = None

    try:
        from src.crawler.base import AsyncCrawler
        from src.startups.startuphub import StartupHubSource
        from src.startups.paginator import StartupHubPaginator
        from src.startups.relevance import StartupRelevanceFilter

        crawler = AsyncCrawler(
            max_concurrency=1
        )

        await crawler.start()

        paginator = StartupHubPaginator(
            source=StartupHubSource,
            crawler=crawler,
            delay_seconds=2,
        )

        relevance_filter = (
            StartupRelevanceFilter()
        )

        checkpoint = StartupCheckpoint(
            CHECKPOINT_PATH
        )

        collector = StartupCollector(
            paginator=paginator,
            relevance_filter=relevance_filter,
            checkpoint=checkpoint,
            target_count=TARGET_COUNT,
        )

        result = await collector.collect()

        accepted = result["accepted"]
        review = result["review"]

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
                accepted,
                file,
                indent=2,
                ensure_ascii=False
            )

        with open(
            REVIEW_OUTPUT_PATH,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                review,
                file,
                indent=2,
                ensure_ascii=False
            )

        print("\n" + "=" * 70)
        print("STARTUP COLLECTION COMPLETE")
        print("=" * 70)

        print(
            "Accepted startups:",
            len(accepted)
        )

        print(
            "Review startups:",
            len(review)
        )

        print(
            "Accepted output:",
            OUTPUT_PATH
        )

        print(
            "Review output:",
            REVIEW_OUTPUT_PATH
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
        collect_startups_1000()
    )
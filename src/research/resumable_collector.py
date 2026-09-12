from src.research.checkpoint import ResearchCheckpoint
from src.research.dedup import ResearchPaperDeduplicator


class ResumableResearchCollector:

    def __init__(
        self,
        paginator,
        checkpoint_file=(
            "data/research_papers_checkpoint.json"
        )
    ):
        self.paginator = paginator

        self.checkpoint = ResearchCheckpoint(
            checkpoint_file
        )

    async def collect(
        self,
        query,
        target_count
    ):
        """
        Collect target_count unique papers.

        If a checkpoint exists for the same query,
        resume from it.
        """

        checkpoint = self.checkpoint.load()

        if checkpoint is not None:

            if checkpoint["query"] != query:
                raise ValueError(
                    "Checkpoint query does not match "
                    "the requested query."
                )

            papers = checkpoint["papers"]
            start = checkpoint["next_start"]

            papers = (
                ResearchPaperDeduplicator.deduplicate(
                    papers
                )
            )

            print(
                f"Resuming from checkpoint: "
                f"{len(papers)} unique papers, "
                f"start={start}"
            )

        else:

            papers = []
            start = 0

            print(
                "No checkpoint found. "
                "Starting from start=0."
            )

        # Already completed
        if len(papers) >= target_count:

            print(
                "Target already reached."
            )

            return papers[:target_count]

        while len(papers) < target_count:

            result = await self.paginator.fetch_page(
                query=query,
                start=start
            )

            page = result["papers"]

            if not page:

                print(
                    "ArXiv returned no more papers."
                )

                break

            papers.extend(page)

            papers = (
                ResearchPaperDeduplicator.deduplicate(
                    papers
                )
            )

            start = result["next_start"]

            # Save immediately after every successfully
            # processed page.
            self.checkpoint.save(
                query=query,
                next_start=start,
                papers=papers
            )

            print(
                f"Checkpoint saved: "
                f"{len(papers)} unique papers, "
                f"next_start={start}"
            )

            if not result["has_more"]:

                print(
                    "Reached the end of the ArXiv results."
                )

                break

        return papers[:target_count]
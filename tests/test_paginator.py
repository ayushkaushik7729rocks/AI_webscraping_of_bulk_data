import pytest

from src.research.paginator import ArxivPaginator


class FakeArxivClient:

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    async def search(self, query, start, max_results):

        self.calls.append({
            "query": query,
            "start": start,
            "max_results": max_results
        })

        page_index = start // max_results

        if page_index >= len(self.pages):
            return []

        return self.pages[page_index]


@pytest.mark.asyncio
async def test_paginator_fetches_multiple_pages():

    pages = [
        [
            {
                "title": "Paper A",
                "paper_url": "https://arxiv.org/abs/1234.0001v1"
            },
            {
                "title": "Paper B",
                "paper_url": "https://arxiv.org/abs/1234.0002v1"
            },
        ],
        [
            {
                "title": "Paper C",
                "paper_url": "https://arxiv.org/abs/1234.0003v1"
            },
            {
                "title": "Paper D",
                "paper_url": "https://arxiv.org/abs/1234.0004v1"
            },
        ],
    ]

    client = FakeArxivClient(pages)

    paginator = ArxivPaginator(
        client=client,
        page_size=2,
        delay_seconds=0
    )

    papers = await paginator.fetch_all(
        query="cat:cs.AI",
        max_papers=4
    )

    assert len(papers) == 4

    assert papers[0]["title"] == "Paper A"
    assert papers[1]["title"] == "Paper B"
    assert papers[2]["title"] == "Paper C"
    assert papers[3]["title"] == "Paper D"

    assert client.calls[0]["start"] == 0
    assert client.calls[1]["start"] == 2


@pytest.mark.asyncio
async def test_paginator_returns_unique_papers():

    pages = [
        [
            {
                "title": "Paper A",
                "paper_url": "https://arxiv.org/abs/1234.0001v1"
            },
            {
                "title": "Paper B",
                "paper_url": "https://arxiv.org/abs/1234.0002v1"
            },
        ],
        [
            {
                "title": "Paper A duplicate version",
                "paper_url": "https://arxiv.org/abs/1234.0001v2"
            },
            {
                "title": "Paper C",
                "paper_url": "https://arxiv.org/abs/1234.0003v1"
            },
        ],
    ]

    client = FakeArxivClient(pages)

    paginator = ArxivPaginator(
        client=client,
        page_size=2,
        delay_seconds=0
    )

    result = await paginator.fetch_all(
        query="cat:cs.AI",
        max_papers=3
    )

    assert len(result) == 3

    assert result[0]["title"] == "Paper A"
    assert result[1]["title"] == "Paper B"
    assert result[2]["title"] == "Paper C"


@pytest.mark.asyncio
async def test_paginator_fetches_extra_page_for_duplicates():

    pages = [
        [
            {
                "title": "Paper A",
                "paper_url": "https://arxiv.org/abs/1234.0001v1"
            },
            {
                "title": "Paper A duplicate",
                "paper_url": "https://arxiv.org/abs/1234.0001v2"
            },
        ],
        [
            {
                "title": "Paper B",
                "paper_url": "https://arxiv.org/abs/1234.0002v1"
            },
            {
                "title": "Paper C",
                "paper_url": "https://arxiv.org/abs/1234.0003v1"
            },
        ],
    ]

    client = FakeArxivClient(pages)

    paginator = ArxivPaginator(
        client=client,
        page_size=2,
        delay_seconds=0
    )

    result = await paginator.fetch_all(
        query="cat:cs.AI",
        max_papers=3
    )

    assert len(result) == 3

    assert result[0]["title"] == "Paper A"
    assert result[1]["title"] == "Paper B"
    assert result[2]["title"] == "Paper C"

    # The paginator needed a second page because
    # the first page contained only one unique paper.
    assert len(client.calls) == 2

@pytest.mark.asyncio
async def test_paginator_fetch_page():

    pages = [
        [
            {
                "title": "Paper A",
                "paper_url": (
                    "https://arxiv.org/abs/1234.0001v1"
                )
            },
            {
                "title": "Paper B",
                "paper_url": (
                    "https://arxiv.org/abs/1234.0002v1"
                )
            },
        ]
    ]

    client = FakeArxivClient(pages)

    paginator = ArxivPaginator(
        client=client,
        page_size=2,
        delay_seconds=0
    )

    result = await paginator.fetch_page(
        query="cat:cs.AI",
        start=0
    )

    assert len(result["papers"]) == 2
    assert result["next_start"] == 2
    assert result["has_more"] is True
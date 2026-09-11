import pytest

from src.research.paginator import ArxivPaginator


class FakeArxivClient:

    def __init__(self):
        self.calls = []

    async def search(
        self,
        query,
        start,
        max_results
    ):

        self.calls.append({
            "query": query,
            "start": start,
            "max_results": max_results
        })

        if start == 0:
            return [
                {"title": "Paper 1"},
                {"title": "Paper 2"},
                {"title": "Paper 3"},
            ]

        if start == 3:
            return [
                {"title": "Paper 4"},
                {"title": "Paper 5"},
                {"title": "Paper 6"},
            ]

        return []


@pytest.mark.asyncio
async def test_paginator_fetches_multiple_pages():

    client = FakeArxivClient()

    paginator = ArxivPaginator(
        client=client,
        page_size=3,
        delay_seconds=0
    )

    papers = await paginator.fetch_all(
        query="cat:cs.AI",
        max_papers=6
    )

    assert len(papers) == 6

    assert papers[0]["title"] == "Paper 1"
    assert papers[-1]["title"] == "Paper 6"

    assert client.calls[0]["start"] == 0
    assert client.calls[1]["start"] == 3
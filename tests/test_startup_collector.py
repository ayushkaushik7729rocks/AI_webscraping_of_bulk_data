import pytest

from src.startups.run_startups_1000 import StartupCollector


class FakeSource:

    def page_url(self, page):
        return f"https://example.com/page/{page}"


class FakePaginator:

    def __init__(self, pages):
        self.pages = pages
        self.requested_pages = []

    async def fetch_page(self, page):
        self.requested_pages.append(page)
        return self.pages.get(page, [])


class FakeRelevanceFilter:

    def classify(self, startup):
        return startup["decision"]

    def filter(self, startups):
        accepted = []
        review = []
        rejected = []

        for startup in startups:
            decision = startup["decision"]

            if decision == "ACCEPT":
                accepted.append(startup)
            elif decision == "REVIEW":
                review.append(startup)
            else:
                rejected.append(startup)

        return {
            "accepted": accepted,
            "review": review,
            "rejected": rejected,
        }


class FakeCheckpoint:

    def __init__(self, state=None):
        self.state = state or {
            "last_completed_page": 0,
            "accepted": [],
            "review": [],
            "seen_urls": [],
        }

        self.saved_states = []

    def load(self):
        return self.state

    def save(self, last_completed_page, accepted, review):
        self.saved_states.append({
            "last_completed_page": last_completed_page,
            "accepted": list(accepted),
            "review": list(review),
        })


def make_startup(name, url, decision):
    return {
        "name": name,
        "source_url": url,
        "decision": decision,
    }


@pytest.mark.asyncio
async def test_collector_stops_when_1000_accepted_are_reached():

    startups = [
        make_startup(
            f"Company {i}",
            f"https://example.com/{i}",
            "ACCEPT"
        )
        for i in range(1000)
    ]

    paginator = FakePaginator({
        1: startups
    })

    checkpoint = FakeCheckpoint()

    collector = StartupCollector(
        paginator=paginator,
        relevance_filter=FakeRelevanceFilter(),
        checkpoint=checkpoint,
        target_count=1000,
    )

    result = await collector.collect()

    assert len(result["accepted"]) == 1000
    assert paginator.requested_pages == [1]

    assert checkpoint.saved_states[-1]["last_completed_page"] == 1


@pytest.mark.asyncio
async def test_collector_keeps_review_separate():

    pages = {
        1: [
            make_startup(
                "Accepted Company",
                "https://example.com/accepted",
                "ACCEPT",
            ),
            make_startup(
                "Review Company",
                "https://example.com/review",
                "REVIEW",
            ),
            make_startup(
                "Rejected Company",
                "https://example.com/rejected",
                "REJECT",
            ),
        ]
    }

    paginator = FakePaginator(pages)
    checkpoint = FakeCheckpoint()

    collector = StartupCollector(
        paginator=paginator,
        relevance_filter=FakeRelevanceFilter(),
        checkpoint=checkpoint,
        target_count=1,
    )

    result = await collector.collect()

    assert len(result["accepted"]) == 1
    assert len(result["review"]) == 1

    assert result["accepted"][0]["name"] == "Accepted Company"
    assert result["review"][0]["name"] == "Review Company"


@pytest.mark.asyncio
async def test_collector_deduplicates_by_source_url():

    duplicate = make_startup(
        "AI Company",
        "https://example.com/ai",
        "ACCEPT",
    )

    pages = {
        1: [duplicate],
        2: [duplicate],
        3: [
            make_startup(
                "Another AI Company",
                "https://example.com/another",
                "ACCEPT",
            )
        ],
    }

    paginator = FakePaginator(pages)
    checkpoint = FakeCheckpoint()

    collector = StartupCollector(
        paginator=paginator,
        relevance_filter=FakeRelevanceFilter(),
        checkpoint=checkpoint,
        target_count=2,
    )

    result = await collector.collect()

    assert len(result["accepted"]) == 2

    urls = [
        startup["source_url"]
        for startup in result["accepted"]
    ]

    assert len(urls) == len(set(urls))


@pytest.mark.asyncio
async def test_collector_resumes_from_checkpoint():

    existing = make_startup(
        "Existing AI Company",
        "https://example.com/existing",
        "ACCEPT",
    )

    pages = {
        3: [
            make_startup(
                "New AI Company",
                "https://example.com/new",
                "ACCEPT",
            )
        ]
    }

    paginator = FakePaginator(pages)

    checkpoint = FakeCheckpoint({
        "last_completed_page": 2,
        "accepted": [existing],
        "review": [],
        "seen_urls": [
            "https://example.com/existing"
        ],
    })

    collector = StartupCollector(
        paginator=paginator,
        relevance_filter=FakeRelevanceFilter(),
        checkpoint=checkpoint,
        target_count=2,
    )

    result = await collector.collect()

    assert paginator.requested_pages == [3]

    assert len(result["accepted"]) == 2

    names = [
        startup["name"]
        for startup in result["accepted"]
    ]

    assert "Existing AI Company" in names
    assert "New AI Company" in names


@pytest.mark.asyncio
async def test_collector_checkpoints_after_each_page():

    pages = {
        1: [
            make_startup(
                "Company 1",
                "https://example.com/1",
                "ACCEPT",
            )
        ],
        2: [
            make_startup(
                "Company 2",
                "https://example.com/2",
                "ACCEPT",
            )
        ],
    }

    paginator = FakePaginator(pages)
    checkpoint = FakeCheckpoint()

    collector = StartupCollector(
        paginator=paginator,
        relevance_filter=FakeRelevanceFilter(),
        checkpoint=checkpoint,
        target_count=2,
    )

    result = await collector.collect()

    assert len(result["accepted"]) == 2

    assert len(checkpoint.saved_states) == 2

    assert (
        checkpoint.saved_states[0]["last_completed_page"]
        == 1
    )

    assert (
        checkpoint.saved_states[1]["last_completed_page"]
        == 2
    )
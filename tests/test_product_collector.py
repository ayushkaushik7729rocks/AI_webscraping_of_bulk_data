import pytest

from src.products.collector import ProductCollector


class FakePaginator:

    def __init__(self, pages):
        self.pages = pages
        self.requested_pages = []

    async def fetch_page(self, page):

        self.requested_pages.append(page)

        return self.pages.get(
            page,
            []
        )


class FakeCheckpoint:

    def __init__(self, state=None):

        self.state = state or {
            "last_completed_page": 0,
            "products": [],
            "seen_urls": [],
        }

        self.saved_states = []

    def load(self):
        return self.state

    def save(
        self,
        last_completed_page,
        products
    ):

        self.saved_states.append(
            {
                "last_completed_page":
                    last_completed_page,

                "products":
                    list(products),
            }
        )

        self.state = {
            "last_completed_page":
                last_completed_page,

            "products":
                list(products),

            "seen_urls": [
                product["source_url"]
                for product in products
                if product.get("source_url")
            ],
        }


def make_product(number):

    return {
        "name": f"Product {number}",
        "rating": 5.0,
        "source_url":
            f"https://example.com/product-{number}",
        "source": "Futurepedia",
    }


@pytest.mark.asyncio
async def test_collector_stops_when_page_has_no_new_products():

    pages = {
        1: [
            make_product(1),
            make_product(2),
        ],

        2: [
            make_product(3),
            make_product(4),
        ],

        3: [
            make_product(3),
            make_product(4),
        ],
    }

    paginator = FakePaginator(pages)

    checkpoint = FakeCheckpoint()

    collector = ProductCollector(
        paginator=paginator,
        checkpoint=checkpoint,
        target_count=1000
    )

    products = await collector.collect()

    assert len(products) == 4

    assert paginator.requested_pages == [
        1,
        2,
        3,
    ]

    assert [
        state["last_completed_page"]
        for state in checkpoint.saved_states
    ] == [
        1,
        2,
    ]

    assert checkpoint.state[
        "last_completed_page"
    ] == 2


@pytest.mark.asyncio
async def test_collector_reaches_target():

    pages = {
        1: [
            make_product(1),
            make_product(2),
            make_product(3),
        ],

        2: [
            make_product(4),
            make_product(5),
            make_product(6),
        ],

        3: [
            make_product(7),
            make_product(8),
            make_product(9),
        ],
    }

    paginator = FakePaginator(pages)

    checkpoint = FakeCheckpoint()

    collector = ProductCollector(
        paginator=paginator,
        checkpoint=checkpoint,
        target_count=8
    )

    products = await collector.collect()

    assert len(products) == 8

    assert paginator.requested_pages == [
        1,
        2,
        3,
    ]


@pytest.mark.asyncio
async def test_collector_deduplicates_urls():

    pages = {
        1: [
            make_product(1),
            make_product(2),
        ],

        2: [
            make_product(2),
            make_product(3),
        ],
    }

    paginator = FakePaginator(pages)

    checkpoint = FakeCheckpoint()

    collector = ProductCollector(
        paginator=paginator,
        checkpoint=checkpoint,
        target_count=3
    )

    products = await collector.collect()

    assert len(products) == 3

    urls = [
        product["source_url"]
        for product in products
    ]

    assert len(urls) == len(set(urls))


@pytest.mark.asyncio
async def test_collector_resumes_from_checkpoint():

    existing_products = [
        make_product(1),
        make_product(2),
    ]

    checkpoint = FakeCheckpoint(
        {
            "last_completed_page": 2,
            "products": existing_products,
            "seen_urls": [
                product["source_url"]
                for product in existing_products
            ],
        }
    )

    pages = {
        3: [
            make_product(3),
            make_product(4),
        ],
    }

    paginator = FakePaginator(pages)

    collector = ProductCollector(
        paginator=paginator,
        checkpoint=checkpoint,
        target_count=4
    )

    products = await collector.collect()

    assert len(products) == 4

    assert paginator.requested_pages == [
        3
    ]


@pytest.mark.asyncio
async def test_collector_checkpoints_every_page():

    pages = {
        1: [
            make_product(1),
        ],

        2: [
            make_product(2),
        ],

        3: [
            make_product(3),
        ],
    }

    paginator = FakePaginator(pages)

    checkpoint = FakeCheckpoint()

    collector = ProductCollector(
        paginator=paginator,
        checkpoint=checkpoint,
        target_count=3
    )

    await collector.collect()

    assert len(
        checkpoint.saved_states
    ) == 3

    assert [
        state["last_completed_page"]
        for state in checkpoint.saved_states
    ] == [
        1,
        2,
        3,
    ]
from src.products.checkpoint import ProductCheckpoint


def test_checkpoint_save_and_load(tmp_path):

    checkpoint_file = (
        tmp_path / "product_checkpoint.json"
    )

    checkpoint = ProductCheckpoint(
        checkpoint_file
    )

    products = [
        {
            "name": "Product A",
            "rating": 5.0,
            "source_url": "https://example.com/product-a",
            "source": "Futurepedia",
        },
        {
            "name": "Product B",
            "rating": 4.5,
            "source_url": "https://example.com/product-b",
            "source": "Futurepedia",
        },
    ]

    checkpoint.save(
        last_completed_page=10,
        products=products
    )

    loaded = checkpoint.load()

    assert loaded["last_completed_page"] == 10

    assert loaded["products"] == products

    assert loaded["seen_urls"] == [
        "https://example.com/product-a",
        "https://example.com/product-b",
    ]


def test_missing_checkpoint_returns_empty_state(
    tmp_path
):

    checkpoint_file = (
        tmp_path / "missing.json"
    )

    checkpoint = ProductCheckpoint(
        checkpoint_file
    )

    loaded = checkpoint.load()

    assert loaded == {
        "last_completed_page": 0,
        "products": [],
        "seen_urls": [],
    }


def test_checkpoint_exists_and_delete(
    tmp_path
):

    checkpoint_file = (
        tmp_path / "product_checkpoint.json"
    )

    checkpoint = ProductCheckpoint(
        checkpoint_file
    )

    assert checkpoint.exists() is False

    checkpoint.save(
        last_completed_page=1,
        products=[]
    )

    assert checkpoint.exists() is True

    checkpoint.delete()

    assert checkpoint.exists() is False
from src.products.producthunt import (
    ProductHuntProductSource
)


SAMPLE_HTML = """
<html>
<body>

<div>
    <a href="/products/wordware">
        <span data-test="product-item-name">
            1. Wordware
        </span>

        <span>
            web-hosted IDE for building AI agents
        </span>
    </a>
</div>

<a href="/products/wordware/alternatives">
    2 alternatives
</a>

<div>
    <a href="/products/wisprflow">
        <span data-test="product-item-name">
            2. Wispr Flow
        </span>

        <span>
            Voice productivity for your writing
        </span>
    </a>
</div>

<a href="/products/wordware">
    Wordware duplicate
</a>

<a href="/other-page">
    Not a product
</a>

</body>
</html>
"""


def test_extract_products():

    products = (
        ProductHuntProductSource.extract_products(
            SAMPLE_HTML,
            "https://www.producthunt.com/products"
        )
    )

    assert len(products) == 2

    assert (
        products[0]["name"]
        == "Wordware"
    )

    assert (
        products[0]["description"]
        == "web-hosted IDE for building AI agents"
    )

    assert (
        products[0]["source_url"]
        == "https://www.producthunt.com/products/wordware"
    )

    assert (
        products[1]["name"]
        == "Wispr Flow"
    )

    assert (
        products[1]["description"]
        == "Voice productivity for your writing"
    )


def test_alternatives_are_ignored():

    products = (
        ProductHuntProductSource.extract_products(
            SAMPLE_HTML,
            "https://www.producthunt.com/products"
        )
    )

    urls = {
        product["source_url"]
        for product in products
    }

    assert (
        "https://www.producthunt.com/products/wordware/alternatives"
        not in urls
    )


def test_duplicate_products_are_removed():

    products = (
        ProductHuntProductSource.extract_products(
            SAMPLE_HTML,
            "https://www.producthunt.com/products"
        )
    )

    urls = [
        product["source_url"]
        for product in products
    ]

    assert len(urls) == len(set(urls))
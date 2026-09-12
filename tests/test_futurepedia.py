from src.products.futurepedia import FuturepediaProductSource


SAMPLE_HTML = """
<html>
<body>

<div class="px-6 pb-2 pt-4 flex h-24 flex-row items-start gap-4">

    <a href="https://www.futurepedia.io/tool/test-tool">
        <div>
            <img alt="Test Tool logo">
        </div>
    </a>

    <div class="flex flex-col items-start">

        <a href="https://www.futurepedia.io/tool/test-tool">
            <p class="m-0 line-clamp-2 overflow-hidden text-xl font-semibold text-slate-700">
                Test Tool
            </p>
        </a>

        <a href="https://www.futurepedia.io/tool/test-tool">
            <div class="flex items-center gap-2 text-lg">
                <span class="sr-only">
                    Rated 4.5 out of 5
                </span>
            </div>
        </a>

    </div>

</div>

</body>
</html>
"""


def test_extract_product():

    products = FuturepediaProductSource.extract_products(
        SAMPLE_HTML,
        "https://www.futurepedia.io/ai-tools/ai-agents"
    )

    assert len(products) == 1

    product = products[0]

    assert product["name"] == "Test Tool"

    assert product["rating"] == 4.5

    assert (
        product["source_url"]
        == "https://www.futurepedia.io/tool/test-tool"
    )

    assert product["source"] == "Futurepedia"


def test_duplicate_product_links_are_removed():

    html = """
    <html>
    <body>

    <div>

        <a href="https://www.futurepedia.io/tool/test-tool">
            <p class="text-xl font-semibold">
                Test Tool
            </p>
        </a>

        <a href="https://www.futurepedia.io/tool/test-tool">
            <p class="text-xl font-semibold">
                Test Tool
            </p>
        </a>

    </div>

    </body>
    </html>
    """

    products = FuturepediaProductSource.extract_products(
        html,
        "https://www.futurepedia.io/ai-tools/ai-agents"
    )

    assert len(products) == 1


def test_invalid_url_is_ignored():

    html = """
    <html>
    <body>

    <a href="https://example.com/tool/test-tool">
        <p class="text-xl font-semibold">
            Invalid Tool
        </p>
    </a>

    </body>
    </html>
    """

    products = FuturepediaProductSource.extract_products(
        html,
        "https://www.futurepedia.io/ai-tools/ai-agents"
    )

    assert len(products) == 0


def test_product_without_rating():

    html = """
    <html>
    <body>

    <div>

        <a href="https://www.futurepedia.io/tool/no-rating">
            <p class="text-xl font-semibold">
                No Rating Tool
            </p>
        </a>

    </div>

    </body>
    </html>
    """

    products = FuturepediaProductSource.extract_products(
        html,
        "https://www.futurepedia.io/ai-tools/ai-agents"
    )

    assert len(products) == 1

    assert products[0]["name"] == "No Rating Tool"

    assert products[0]["rating"] is None
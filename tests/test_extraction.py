from src.extraction.html_parser import HTMLExtractor


def test_extract_metadata():

    html = """
    <html>
        <head>

            <title>Test AI Startup</title>

            <meta
                name="description"
                content="An AI startup building useful tools."
            >

            <link
                rel="canonical"
                href="https://example.com/startup"
            >

            <meta
                property="og:url"
                content="https://example.com/startup"
            >

        </head>

        <body>
            <h1>Test AI Startup</h1>
        </body>
    </html>
    """

    extractor = HTMLExtractor()

    result = extractor.extract_metadata(
        html,
        "https://example.com/startup"
    )

    assert result["url"] == "https://example.com/startup"

    assert result["title"] == "Test AI Startup"

    assert (
        result["description"]
        == "An AI startup building useful tools."
    )

    assert (
        result["canonical_url"]
        == "https://example.com/startup"
    )

    assert (
        result["og_url"]
        == "https://example.com/startup"
    )

def test_extract_published_date():

    html = """
    <html>
        <head>

            <title>AI News</title>

            <meta
                property="article:published_time"
                content="2026-09-11T08:30:00Z"
            >

        </head>

        <body>
            <h1>AI News</h1>
        </body>
    </html>
    """

    extractor = HTMLExtractor()

    result = extractor.extract_metadata(
        html,
        "https://example.com/news"
    )

    assert result["published_date"] == (
        "2026-09-11T08:30:00+00:00"
    )

def test_parse_relative_date():

    extractor = HTMLExtractor()

    result = extractor.parse_date(
        "2 hours ago"
    )

    assert result is not None

def test_extract_main_text():

    html = """
    <html>
        <head>
            <title>AI News</title>
        </head>

        <body>

            <nav>
                Home About Contact
            </nav>

            <article>
                <h1>AI Startup Raises Funding</h1>

                <p>
                    An AI startup has raised new funding.
                </p>

                <p>
                    The company will use the funding
                    to expand its research team.
                </p>
            </article>

            <footer>
                Copyright 2026
            </footer>

        </body>
    </html>
    """

    extractor = HTMLExtractor()

    result = extractor.extract_metadata(
        html,
        "https://example.com/news"
    )

    assert "AI Startup Raises Funding" in result["main_text"]

    assert (
        "An AI startup has raised new funding."
        in result["main_text"]
    )

    assert "Home About Contact" not in result["main_text"]
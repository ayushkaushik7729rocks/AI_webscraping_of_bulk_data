from src.startups.wellfound import (
    WellfoundStartupSource
)
from src.startups.extractor import (
    StartupExtractor
)
from src.startups.dedup import (
    StartupDeduplicator
)


def test_wellfound_page_url():

    assert (
        WellfoundStartupSource.page_url(1)
        == (
            "https://wellfound.com/startups/"
            "industry/artificial-intelligence"
        )
    )

    assert (
        WellfoundStartupSource.page_url(2)
        == (
            "https://wellfound.com/startups/"
            "industry/artificial-intelligence?page=2"
        )
    )


def test_extract_startup_links():

    html = """
    <html>
        <body>
            <a href="/company/openai">
                OpenAI
            </a>

            <a href="/company/anthropic">
                Anthropic
            </a>

            <a href="/other/page">
                Ignore Me
            </a>
        </body>
    </html>
    """

    startups = (
        WellfoundStartupSource.extract_startups(
            html,
            "https://wellfound.com/test"
        )
    )

    assert len(startups) == 2

    assert startups[0]["name"] == "OpenAI"

    assert (
        startups[0]["source_url"]
        == "https://wellfound.com/company/openai"
    )

    assert startups[1]["name"] == "Anthropic"


def test_extract_duplicate_links():

    html = """
    <a href="/company/openai">OpenAI</a>
    <a href="/company/openai">OpenAI</a>
    """

    startups = (
        WellfoundStartupSource.extract_startups(
            html,
            "https://wellfound.com/test"
        )
    )

    assert len(startups) == 1


def test_startup_validation():

    startup = {
        "name": "OpenAI",
        "source_url": (
            "https://wellfound.com/company/openai"
        ),
        "source": "Wellfound",
    }

    assert StartupExtractor.validate(
        startup
    )


def test_startup_validation_requires_source():

    startup = {
        "name": "OpenAI",
        "source_url": (
            "https://wellfound.com/company/openai"
        ),
    }

    assert not StartupExtractor.validate(
        startup
    )


def test_startup_url_normalization():

    startup = {
        "name": "OpenAI ",
        "source_url": (
            "HTTPS://Wellfound.com/company/openai/"
        ),
        "source": "Wellfound",
    }

    cleaned = StartupExtractor.clean(
        startup
    )

    assert cleaned["name"] == "OpenAI"

    assert (
        cleaned["source_url"]
        == "https://wellfound.com/company/openai"
    )


def test_startup_deduplication():

    startups = [
        {
            "name": "OpenAI",
            "source_url": (
                "https://wellfound.com/company/openai"
            ),
            "source": "Wellfound",
        },
        {
            "name": "OpenAI",
            "source_url": (
                "https://wellfound.com/company/openai"
            ),
            "source": "Wellfound",
        },
        {
            "name": "Anthropic",
            "source_url": (
                "https://wellfound.com/company/anthropic"
            ),
            "source": "Wellfound",
        },
    ]

    unique = StartupDeduplicator.deduplicate(
        startups
    )

    assert len(unique) == 2
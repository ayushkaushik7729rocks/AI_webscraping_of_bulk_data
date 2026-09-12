from src.startups.startuphub import StartupHubSource


SAMPLE_HTML = """
<html>
<body>

<a href="/startups/01health">
    <span aria-hidden="true">
        0
    </span>

    <span>
        <span class="block truncate text-sm font-medium text-foreground">
            01Health
        </span>

        <span class="text-xs text-muted-foreground">
            HealthTech · London, United Kingdom · $15.0M
        </span>

        <span class="text-xs">
            A healthcare technology company.
        </span>
    </span>
</a>


<a href="/startups/0g-labs">
    <img src="logo.png">

    <span>
        <span class="block truncate text-sm font-medium text-foreground">
            0G Labs
        </span>

        <span class="text-xs text-muted-foreground">
            AI · San Francisco, United States · $75.0M
        </span>

        <span class="text-xs">
            Building a decentralized AI operating system.
        </span>
    </span>
</a>


<a href="/search">
    Search
</a>

</body>
</html>
"""


def get_startups():
    return StartupHubSource.extract_startups(
        SAMPLE_HTML,
        "https://www.startuphub.ai/startups"
    )


def test_extract_startups_gets_company_names():

    startups = get_startups()

    assert len(startups) == 2

    assert startups[0]["name"] == "01Health"
    assert startups[1]["name"] == "0G Labs"


def test_extract_startups_extracts_category():

    startups = get_startups()

    assert startups[0]["category"] == "HealthTech"
    assert startups[1]["category"] == "AI"


def test_extract_startups_extracts_location():

    startups = get_startups()

    assert (
        startups[0]["location"]
        == "London, United Kingdom"
    )

    assert (
        startups[1]["location"]
        == "San Francisco, United States"
    )


def test_extract_startups_extracts_funding():

    startups = get_startups()

    assert startups[0]["funding"] == "$15.0M"
    assert startups[1]["funding"] == "$75.0M"


def test_extract_startups_extracts_description():

    startups = get_startups()

    assert (
        startups[0]["description"]
        == "A healthcare technology company."
    )

    assert (
        startups[1]["description"]
        == "Building a decentralized AI operating system."
    )


def test_extract_startups_does_not_include_metadata_in_name():

    startups = get_startups()

    names = [
        startup["name"]
        for startup in startups
    ]

    assert "01Health" in names
    assert "0G Labs" in names

    assert "HealthTech" not in names
    assert "San Francisco" not in names
    assert "$75.0M" not in names


def test_extract_startups_only_accepts_startup_urls():

    startups = get_startups()

    for startup in startups:

        assert startup["source_url"].startswith(
            "https://www.startuphub.ai/startups/"
        )


def test_extract_startups_deduplicates_urls():

    html = SAMPLE_HTML + """
    <a href="/startups/0g-labs">
        <span>
            <span class="block truncate text-sm font-medium text-foreground">
                0G Labs
            </span>
        </span>
    </a>
    """

    startups = StartupHubSource.extract_startups(
        html,
        "https://www.startuphub.ai/startups"
    )

    urls = [
        startup["source_url"]
        for startup in startups
    ]

    assert len(urls) == len(set(urls))
    assert len(startups) == 2
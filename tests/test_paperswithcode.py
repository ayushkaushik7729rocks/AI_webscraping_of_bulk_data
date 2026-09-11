from src.research.paperswithcode import PapersWithCodeClient


def test_extract_github_urls():

    html = """
    <html>
        <body>

            <a href="https://github.com/example/project">
                Code
            </a>

            <a href="https://github.com/example/another-project">
                Implementation
            </a>

            <a href="https://example.com/not-github">
                Other
            </a>

        </body>
    </html>
    """

    urls = PapersWithCodeClient.extract_github_urls(
        html
    )

    assert urls == [
        "https://github.com/example/another-project",
        "https://github.com/example/project"
    ]


def test_extract_github_urls_when_none_exist():

    html = """
    <html>
        <body>

            <a href="https://example.com/project">
                Project
            </a>

        </body>
    </html>
    """

    urls = PapersWithCodeClient.extract_github_urls(
        html
    )

    assert urls == []


def test_extract_github_urls_ignores_organizations():

    html = """
    <html>
        <body>

            <a href="https://github.com/huggingface">
                Organization
            </a>

            <a href="https://github.com/huggingface/transformers">
                Repository
            </a>

        </body>
    </html>
    """

    urls = PapersWithCodeClient.extract_github_urls(
        html
    )

    assert urls == [
        "https://github.com/huggingface/transformers"
    ]
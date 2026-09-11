from src.research.arxiv import ArxivClient


def test_parse_arxiv_response():

    xml = """<?xml version="1.0" encoding="UTF-8"?>
    
    <feed
        xmlns="http://www.w3.org/2005/Atom"
    >

        <entry>

            <id>
                https://arxiv.org/abs/2609.12345
            </id>

            <title>
                A Test AI Paper
            </title>

            <published>
                2026-09-10T12:00:00Z
            </published>

            <link
                rel="alternate"
                type="text/html"
                href="https://arxiv.org/abs/1234.5678"/>

            <link
                title="pdf"
                rel="related"
                type="application/pdf"
                href="https://arxiv.org/pdf/1234.5678"/>

            <summary>
                This is a test paper about AI.
            </summary>

            <author>
                <name>John Smith</name>
            </author>

            <author>
                <name>Jane Doe</name>
            </author>

        </entry>

    </feed>
    """

    # We don't need a crawler for testing
    # the XML parser itself.
    client = ArxivClient(None)

    papers = client.parse_response(xml)

    assert len(papers) == 1

    paper = papers[0]

    assert paper["title"] == "A Test AI Paper"

    assert paper["authors"] == [
        "John Smith",
        "Jane Doe",
    ]

    assert (
        paper["paper_url"]
        == "https://arxiv.org/abs/2609.12345"
    )

    assert (
        paper["published_date"]
        == "2026-09-10T12:00:00Z"
    )

    assert len(papers[0]["links"]) == 2

    assert papers[0]["links"][0]["href"] == \
        "https://arxiv.org/abs/1234.5678"

    assert papers[0]["links"][1]["title"] == "pdf"
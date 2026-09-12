from bs4 import BeautifulSoup


class StartupHubSource:
    BASE_URL = "https://www.startuphub.ai/startups"

    @classmethod
    def page_url(cls, page):
        if page <= 1:
            return cls.BASE_URL

        return f"{cls.BASE_URL}/page/{page}"

    @staticmethod
    def _extract_card_metadata(link):
        """
        Extract structured metadata from one StartupHub
        startup card.

        Expected structure:

        <a href="/startups/...">
            <img ...> OR <span ...>icon</span>

            <span>
                <span class="... text-sm font-medium text-foreground">
                    Company Name
                </span>

                <span class="... text-xs ...">
                    Category · Location · Funding
                </span>

                <span class="... text-xs ...">
                    Description
                </span>
            </span>
        </a>
        """

        name_element = link.select_one(
            "span.text-sm.font-medium.text-foreground"
        )

        if not name_element:
            return None

        name = name_element.get_text(
            " ",
            strip=True
        )

        if not name:
            return None

        # The company name is inside the main content container.
        content_container = name_element.parent

        if not content_container:
            return None

        metadata_elements = content_container.find_all(
            "span",
            recursive=False
        )

        metadata_text = None
        description = None

        if len(metadata_elements) >= 2:
            metadata_text = metadata_elements[1].get_text(
                " ",
                strip=True
            )

        if len(metadata_elements) >= 3:
            description = metadata_elements[2].get_text(
                " ",
                strip=True
            )

        return {
            "name": name,
            "metadata": metadata_text,
            "description": description,
        }

    @staticmethod
    def _parse_metadata(metadata):
        """
        Parse:

            Category · Location · Funding

        into separate fields.

        Some cards do not contain all three fields,
        so missing values remain None.
        """

        if not metadata:
            return {
                "category": None,
                "location": None,
                "funding": None,
            }

        parts = [
            part.strip()
            for part in metadata.split("·")
            if part.strip()
        ]

        category = None
        location = None
        funding = None

        if len(parts) >= 1:
            category = parts[0]

        if len(parts) >= 2:
            location = parts[1]

        if len(parts) >= 3:
            funding = " · ".join(parts[2:])

        return {
            "category": category,
            "location": location,
            "funding": funding,
        }

    @classmethod
    def extract_startups(cls, html, source_url):
        soup = BeautifulSoup(html, "lxml")

        startups = []
        seen_urls = set()

        for link in soup.find_all("a", href=True):

            href = link["href"].strip()

            if not href.startswith("/startups/"):
                continue

            startup_path = (
                href
                .split("?")[0]
                .split("#")[0]
                .rstrip("/")
            )

            if startup_path == "/startups":
                continue

            startup_url = (
                "https://www.startuphub.ai"
                + startup_path
            )

            if startup_url in seen_urls:
                continue

            card = cls._extract_card_metadata(link)

            if not card:
                continue

            metadata = cls._parse_metadata(
                card["metadata"]
            )

            seen_urls.add(startup_url)

            startups.append({
                "name": card["name"],
                "category": metadata["category"],
                "location": metadata["location"],
                "funding": metadata["funding"],
                "description": card["description"],
                "source_url": startup_url,
                "source": "StartupHub.ai",
            })

        return startups
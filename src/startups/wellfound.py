from bs4 import BeautifulSoup


class WellfoundStartupSource:

    BASE_URL = (
        "https://wellfound.com/startups/"
        "industry/artificial-intelligence"
    )

    @classmethod
    def page_url(cls, page):
        if page <= 1:
            return cls.BASE_URL

        return f"{cls.BASE_URL}?page={page}"

    @staticmethod
    def extract_startups(html, source_url):
        """
        Extract startup cards from a Wellfound page.

        This parser intentionally extracts only fields that
        are visibly present in the source page.
        """

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        startups = []

        # Wellfound exposes startup profile links
        # throughout the category page.
        seen_urls = set()

        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link["href"].strip()

            if not href.startswith("/company/"):
                continue

            startup_url = (
                "https://wellfound.com"
                + href.split("?")[0]
            )

            if startup_url in seen_urls:
                continue

            name = link.get_text(
                " ",
                strip=True
            )

            if not name:
                continue

            seen_urls.add(startup_url)

            startups.append({
                "name": name,
                "source_url": startup_url,
                "source": "Wellfound",
            })

        return startups
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


class FuturepediaProductSource:

    BASE_URL = "https://www.futurepedia.io/ai-tools"

    @classmethod
    def page_url(cls, page, category="ai-agents"):
        if page <= 1:
            return f"{cls.BASE_URL}/{category}"

        return f"{cls.BASE_URL}/{category}?page={page}"

    @staticmethod
    def _normalize_product_url(url):
        if not url:
            return None

        parsed = urlparse(url)

        if parsed.netloc.lower() != "www.futurepedia.io":
            return None

        path = parsed.path.rstrip("/")

        if not path.startswith("/tool/"):
            return None

        return f"https://www.futurepedia.io{path}"

    @staticmethod
    def _extract_product_name(link):
        name_element = link.find(
            "p",
            class_=lambda value: (
                value
                and "text-xl" in value
                and "font-semibold" in value
            )
        )

        if not name_element:
            return None

        name = name_element.get_text(
            " ",
            strip=True
        )

        return name or None

    @staticmethod
    def _extract_rating(container):
        rating_element = container.find(
            "span",
            class_="sr-only"
        )

        if not rating_element:
            return None

        text = rating_element.get_text(
            " ",
            strip=True
        )

        match = re.search(
            r"Rated\s+([\d.]+)\s+out\s+of\s+5",
            text,
            re.IGNORECASE
        )

        if not match:
            return None

        return float(match.group(1))

    @staticmethod
    def inspect_product(html):
        soup = BeautifulSoup(
            html,
            "lxml"
        )

        product_links = []

        for link in soup.find_all(
            "a",
            href=True
        ):
            href = link["href"]

            if "/tool/" in href:
                product_links.append(link)

        print(
            "Matching product-like links:",
            len(product_links)
        )

        for index, link in enumerate(
            product_links,
            start=1
        ):
            print(
                "\n" + "=" * 70
            )

            print(
                f"LINK {index}"
            )

            print(
                "=" * 70
            )

            print(
                link.prettify()
            )

            parent = link.parent

            if parent:
                print(
                    "\nPARENT:"
                )

                print(
                    parent.prettify()
                )

    @classmethod
    def extract_products(
        cls,
        html,
        source_url
    ):
        soup = BeautifulSoup(
            html,
            "lxml"
        )

        products = []
        seen_urls = set()

        for link in soup.find_all(
            "a",
            href=True
        ):

            product_url = cls._normalize_product_url(
                link["href"]
            )

            if not product_url:
                continue

            if product_url in seen_urls:
                continue

            name = cls._extract_product_name(
                link
            )

            if not name:
                continue

            container = link.parent

            rating = cls._extract_rating(
                container
            )

            seen_urls.add(
                product_url
            )

            products.append(
                {
                    "name": name,
                    "rating": rating,
                    "source_url": product_url,
                    "source": "Futurepedia",
                    "category_url": source_url,
                }
            )

        return products
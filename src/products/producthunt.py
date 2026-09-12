import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


class ProductHuntProductSource:

    BASE_URL = (
        "https://www.producthunt.com/products"
        "?parentTopic=development"
        "&period=all-time"
        "&topic=artificial-intelligence"
    )

    @classmethod
    def page_url(cls, page):
        if page <= 1:
            return cls.BASE_URL

        return f"{cls.BASE_URL}&page={page}"

    @staticmethod
    def _normalize_product_url(href):

        if not href:
            return None

        if href.startswith("/"):
            url = (
                "https://www.producthunt.com"
                + href
            )
        else:
            url = href

        parsed = urlparse(url)

        if parsed.netloc.lower() != "www.producthunt.com":
            return None

        path = parsed.path.rstrip("/")

        match = re.fullmatch(
            r"/products/([^/]+)",
            path
        )

        if not match:
            return None

        slug = match.group(1)

        return (
            "https://www.producthunt.com"
            f"/products/{slug}"
        )

    @staticmethod
    def _extract_product_name(name_element):

        text = name_element.get_text(
            " ",
            strip=True
        )

        if not text:
            return None

        # Example:
        # "1. Wordware"
        #
        # becomes:
        # "Wordware"

        text = re.sub(
            r"^\d+\.\s*",
            "",
            text
        )

        return text.strip() or None

    @staticmethod
    def _extract_description(name_element):

        parent_link = name_element.find_parent(
            "a"
        )

        if not parent_link:
            return None

        spans = parent_link.find_all(
            "span"
        )

        for span in spans:

            if span is name_element:
                continue

            text = span.get_text(
                " ",
                strip=True
            )

            if text:
                return text

        return None

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

        name_elements = soup.find_all(
            "span",
            attrs={
                "data-test": "product-item-name"
            }
        )

        for name_element in name_elements:

            parent_link = name_element.find_parent(
                "a",
                href=True
            )

            if not parent_link:
                continue

            product_url = (
                cls._normalize_product_url(
                    parent_link["href"]
                )
            )

            if not product_url:
                continue

            if product_url in seen_urls:
                continue

            name = cls._extract_product_name(
                name_element
            )

            if not name:
                continue

            description = (
                cls._extract_description(
                    name_element
                )
            )

            seen_urls.add(product_url)

            products.append(
                {
                    "name": name,
                    "description": description,
                    "source_url": product_url,
                    "source": "Product Hunt",
                    "category_url": source_url,
                }
            )

        return products
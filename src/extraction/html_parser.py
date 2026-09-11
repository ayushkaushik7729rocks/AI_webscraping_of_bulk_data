from bs4 import BeautifulSoup
from dateparser import parse


class HTMLExtractor:

    def extract_metadata(self, html: str, url: str):

        soup = BeautifulSoup(html, "lxml")

        title = None

        if soup.title:
            title = soup.title.get_text(strip=True)

        description = None

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if description_tag:
            description = description_tag.get("content")

        canonical_url = None

        canonical_tag = soup.find(
            "link",
            attrs={"rel": "canonical"}
        )

        if canonical_tag:
            canonical_url = canonical_tag.get("href")

        og_url = None

        og_url_tag = soup.find(
            "meta",
            attrs={"property": "og:url"}
        )

        if og_url_tag:
            og_url = og_url_tag.get("content")

        published_date = self.extract_published_date(soup)
        main_text = self.extract_main_text(soup)


        return {
            "url": url,
            "title": title,
            "description": description,
            "canonical_url": canonical_url,
            "og_url": og_url,
            "published_date": published_date,
            "main_text": main_text,

        }

    def extract_published_date(self, soup):

        # 1. article:published_time
        tag = soup.find(
            "meta",
            attrs={"property": "article:published_time"}
        )

        if tag and tag.get("content"):
            return self.parse_date(tag["content"])

        # 2. og:published_time
        tag = soup.find(
            "meta",
            attrs={"property": "og:published_time"}
        )

        if tag and tag.get("content"):
            return self.parse_date(tag["content"])

        # 3. meta[name="date"]
        tag = soup.find(
            "meta",
            attrs={"name": "date"}
        )

        if tag and tag.get("content"):
            return self.parse_date(tag["content"])

        # 4. <time datetime="...">
        tag = soup.find("time")

        if tag:

            datetime_value = tag.get("datetime")

            if datetime_value:
                parsed = self.parse_date(datetime_value)

                if parsed:
                    return parsed

            # 5. visible text inside <time>
            text = tag.get_text(" ", strip=True)

            if text:
                parsed = self.parse_date(text)

                if parsed:
                    return parsed

        return None

    def parse_date(self, value):

        parsed = parse(
            value,
            settings={
                "RETURN_AS_TIMEZONE_AWARE": True,
                "TIMEZONE": "UTC",
                "TO_TIMEZONE": "UTC",
            }
        )

        if parsed is None:
            return None

        return parsed.isoformat()

    def extract_main_text(self, soup):

    # Prefer semantic article content.
        article = soup.find("article")

        if article:
            return article.get_text(
                " ",
                strip=True
            )

    # Fall back to the main element.
        main = soup.find("main")

        if main:
            return main.get_text(
                " ",
                strip=True
            )

    # Last resort: use body.
        body = soup.find("body")

        if body:
            return body.get_text(
                " ",
                strip=True
            )

        return ""
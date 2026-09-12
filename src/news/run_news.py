import asyncio
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import aiohttp
from bs4 import BeautifulSoup

from src.crawler.base import AsyncCrawler


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = Path("data/news.json")

MAX_AGE_HOURS = 24

# Five AI-focused news sources.
RSS_FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
    },
    {
        "name": "DeepLearning.AI - The Batch",
        "url": "https://www.deeplearning.ai/the-batch/feed/",
    },
]


# ============================================================
# HELPERS
# ============================================================

def parse_date(value):
    """
    Convert common RSS/Atom date formats into UTC datetime.
    """

    if not value:
        return None

    value = value.strip()

    # RFC 2822 / RSS date.
    try:
        dt = parsedate_to_datetime(value)

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(timezone.utc)

    except (TypeError, ValueError, OverflowError):
        pass

    # ISO 8601 / Atom date.
    try:
        normalized = value.replace(
            "Z",
            "+00:00"
        )

        dt = datetime.fromisoformat(
            normalized
        )

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(timezone.utc)

    except (TypeError, ValueError):
        return None


def normalize_url(url):

    if not url:
        return None

    url = url.strip()

    parsed = urlparse(url)

    if not parsed.scheme:
        return None

    if parsed.scheme not in {
        "http",
        "https",
    }:
        return None

    # Remove tracking parameters.
    query_parts = []

    if parsed.query:

        for part in parsed.query.split("&"):

            key = part.split("=")[0].lower()

            if key.startswith("utm_"):
                continue

            if key in {
                "fbclid",
                "gclid",
                "mc_cid",
                "mc_eid",
            }:
                continue

            query_parts.append(part)

    query = "&".join(query_parts)

    normalized = urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            query,
            "",
        )
    )

    return normalized


def clean_text(value):

    if not value:
        return None

    soup = BeautifulSoup(
        value,
        "lxml"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip() or None


def content_hash(title, description):

    text = (
        (title or "") +
        "\n" +
        (description or "")
    ).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()


def extract_element_text(element):

    if element is None:
        return None

    return clean_text(
        element.get_text(
            " ",
            strip=True
        )
    )


def find_first_text(element, names):

    for name in names:

        child = element.find(
            name
        )

        if child is not None:

            text = extract_element_text(
                child
            )

            if text:
                return text

    return None


# ============================================================
# RSS PARSER
# ============================================================

def parse_feed(
    xml_text,
    source_name,
    source_feed_url
):

    soup = BeautifulSoup(
        xml_text,
        "xml"
    )

    items = soup.find_all(
        ["item", "entry"]
    )

    records = []

    for item in items:

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = find_first_text(
            item,
            ["title"]
        )

        if not title:
            continue

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        url = None

        link = item.find(
            "link"
        )

        if link:

            # RSS:
            # <link>https://...</link>
            if link.get_text(
                strip=True
            ):
                url = link.get_text(
                    strip=True
                )

            # Atom:
            # <link href="..."/>
            if not url:
                url = link.get(
                    "href"
                )

        # Some feeds use guid as fallback.
        if not url:

            guid = item.find(
                "guid"
            )

            if guid:
                url = guid.get_text(
                    strip=True
                )

        url = normalize_url(
            url
        )

        if not url:
            continue

        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------

        description = None

        for tag_name in [
            "description",
            "summary",
            "content",
            "content:encoded",
        ]:

            element = item.find(
                tag_name
            )

            if element is not None:

                description = clean_text(
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

                if description:
                    break

        # ----------------------------------------------------
        # Published date
        # ----------------------------------------------------

        published_raw = None

        for tag_name in [
            "pubDate",
            "published",
            "updated",
            "date",
            "dc:date",
        ]:

            element = item.find(
                tag_name
            )

            if element is not None:

                published_raw = (
                    element.get_text(
                        strip=True
                    )
                )

                if published_raw:
                    break

        published_at = parse_date(
            published_raw
        )

        # ----------------------------------------------------
        # Author
        # ----------------------------------------------------

        author = None

        for tag_name in [
            "author",
            "dc:creator",
        ]:

            element = item.find(
                tag_name
            )

            if element is not None:

                author = extract_element_text(
                    element
                )

                if author:
                    break

        # ----------------------------------------------------
        # Build record
        # ----------------------------------------------------

        records.append(
            {
                "schemaVersion": "1.0",
                "recordType": "news",

                "source": {
                    "name": source_name,
                    "url": source_feed_url,
                },

                "content": {
                    "title": title,
                    "description": description,
                    "url": url,
                    "author": author,
                    "published_at": (
                        published_at.isoformat()
                        if published_at
                        else None
                    ),
                },

                "collected_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),

                "content_hash": content_hash(
                    title,
                    description
                ),
            }
        )

    return records


# ============================================================
# FRESHNESS
# ============================================================

def is_fresh(record, now=None):

    if now is None:
        now = datetime.now(
            timezone.utc
        )

    published_at = (
        record
        .get("content", {})
        .get("published_at")
    )

    if not published_at:
        return False

    try:
        published = datetime.fromisoformat(
            published_at
        )

    except ValueError:
        return False

    if published.tzinfo is None:
        published = published.replace(
            tzinfo=timezone.utc
        )

    published = published.astimezone(
        timezone.utc
    )

    # Reject future dates.
    if published > now:
        return False

    age = now - published

    return age <= timedelta(
        hours=MAX_AGE_HOURS
    )


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate(records):

    unique = []

    seen_urls = set()
    seen_hashes = set()

    for record in records:

        content = record.get(
            "content",
            {}
        )

        url = content.get(
            "url"
        )

        record_hash = record.get(
            "content_hash"
        )

        # URL is strongest identity.
        if url and url in seen_urls:
            continue

        # Content hash catches syndicated duplicates.
        if record_hash and record_hash in seen_hashes:
            continue

        if url:
            seen_urls.add(url)

        if record_hash:
            seen_hashes.add(record_hash)

        unique.append(record)

    return unique


# ============================================================
# FETCH ONE FEED
# ============================================================

async def fetch_feed(
    crawler,
    source
):

    print(
        f"\nFetching: {source['name']}"
    )

    result = await crawler.fetch(
        source["url"],
        headers={
            "Accept": (
                "application/rss+xml, "
                "application/atom+xml, "
                "application/xml, "
                "text/xml, "
                "text/html;q=0.9"
            )
        }
    )

    if result["status"] != 200:

        print(
            f"FAILED: "
            f"{source['name']} "
            f"status={result['status']}"
        )

        return []

    records = parse_feed(
        result["html"],
        source["name"],
        source["url"]
    )

    print(
        f"Fetched {len(records)} articles"
    )

    return records


# ============================================================
# SAVE
# ============================================================

def save_records(records):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 70)
    print("FRONTIER ATLAS — AI NEWS COLLECTION")
    print("=" * 70)

    now = datetime.now(
        timezone.utc
    )

    crawler = AsyncCrawler(
        max_concurrency=5,
        max_retries=3
    )

    await crawler.start()

    try:

        # Fetch all five feeds concurrently.
        results = await asyncio.gather(
            *[
                fetch_feed(
                    crawler,
                    source
                )
                for source in RSS_FEEDS
            ]
        )

    finally:

        await crawler.close()

    all_records = []

    for records in results:
        all_records.extend(records)

    print(
        f"\nTotal fetched: "
        f"{len(all_records)}"
    )

    # --------------------------------------------------------
    # Freshness
    # --------------------------------------------------------

    fresh_records = [
        record
        for record in all_records
        if is_fresh(
            record,
            now
        )
    ]

    print(
        f"Within last 24 hours: "
        f"{len(fresh_records)}"
    )

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    unique_records = deduplicate(
        fresh_records
    )

    # Sort newest first.
    unique_records.sort(
        key=lambda record: (
            record
            .get("content", {})
            .get("published_at")
            or ""
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_records(
        unique_records
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    missing_url = sum(
        1
        for record in unique_records
        if not record
        .get("content", {})
        .get("url")
    )

    missing_title = sum(
        1
        for record in unique_records
        if not record
        .get("content", {})
        .get("title")
    )

    missing_date = sum(
        1
        for record in unique_records
        if not record
        .get("content", {})
        .get("published_at")
    )

    print("\n" + "=" * 70)
    print("NEWS COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"Fetched: {len(all_records)}"
    )

    print(
        f"Fresh (<24h): "
        f"{len(fresh_records)}"
    )

    print(
        f"Unique: "
        f"{len(unique_records)}"
    )

    print(
        f"Missing URLs: "
        f"{missing_url}"
    )

    print(
        f"Missing titles: "
        f"{missing_title}"
    )

    print(
        f"Missing published dates: "
        f"{missing_date}"
    )

    print(
        f"Output: "
        f"{OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # Source breakdown
    # --------------------------------------------------------

    counts = {}

    for record in unique_records:

        source = (
            record
            .get("source", {})
            .get("name", "unknown")
        )

        counts[source] = (
            counts.get(source, 0) + 1
        )

    print("\nSource breakdown:")

    for source, count in sorted(
        counts.items()
    ):

        print(
            f"  {source}: {count}"
        )


if __name__ == "__main__":
    asyncio.run(main())
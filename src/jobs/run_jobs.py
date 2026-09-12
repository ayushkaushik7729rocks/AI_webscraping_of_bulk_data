import asyncio
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup

from src.crawler.base import AsyncCrawler


# ============================================================
# CONFIG
# ============================================================

OUTPUT_FILE = Path("data/jobs.json")

MAX_AGE_HOURS = 24

# Public RSS feeds.
# These are intentionally RSS-first so that publication dates
# come directly from the source instead of being guessed from
# page appearance.
JOB_SOURCES = [
    {
        "name": "Remote OK",
        "url": "https://remoteok.com/remote-jobs.rss",
    },
    {
        "name": "We Work Remotely",
        "url": "https://weworkremotely.com/remote-jobs.rss",
    },
    {
        "name": "Remotive",
        "url": "https://remotive.com/feed",
    },
    {
        "name": "Remote First Jobs - AI",
        "url": "https://remotefirstjobs.com/rss/jobs/ai.rss",
    },
    {
        "name": "AIJobs.net",
        "url": "https://aijobs.net/feed/",
    },
]


# ============================================================
# DATE PARSING
# ============================================================

def parse_date(value):

    if not value:
        return None

    value = value.strip()

    # RSS / RFC 2822
    try:

        dt = parsedate_to_datetime(
            value
        )

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        )

    except (
        TypeError,
        ValueError,
        OverflowError
    ):
        pass

    # ISO 8601 / Atom
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

        return dt.astimezone(
            timezone.utc
        )

    except (
        TypeError,
        ValueError
    ):
        return None


# ============================================================
# TEXT / URL HELPERS
# ============================================================

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


def normalize_url(url):

    if not url:
        return None

    url = url.strip()

    parsed = urlparse(url)

    if parsed.scheme not in {
        "http",
        "https"
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

    query = "&".join(
        query_parts
    )

    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            query,
            "",
        )
    )


def make_content_hash(
    title,
    company,
    description
):

    text = " ".join(
        [
            title or "",
            company or "",
            description or "",
        ]
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip().lower()

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================
# RSS EXTRACTION
# ============================================================

def get_child_text(
    item,
    names
):

    for name in names:

        element = item.find(
            name
        )

        if element is None:
            continue

        text = element.get_text(
            " ",
            strip=True
        )

        if text:
            return text

    return None


def get_link(item):

    link = item.find(
        "link"
    )

    if link is not None:

        text = link.get_text(
            strip=True
        )

        if text:
            return text

        href = link.get(
            "href"
        )

        if href:
            return href

    guid = item.find(
        "guid"
    )

    if guid is not None:

        text = guid.get_text(
            strip=True
        )

        if text.startswith(
            (
                "http://",
                "https://"
            )
        ):
            return text

    return None


def extract_company(
    title,
    description
):

    if not title:
        return None

    # Common patterns:
    #
    # "AI Engineer at Company"
    # "AI Engineer - Company"
    # "Company: AI Engineer"
    #
    # This is intentionally conservative.
    # We do not want to fabricate a company.

    patterns = [
        r"\bat\s+(.+)$",
        r"\s+-\s+([^-|]+)$",
        r"^([^:]+):\s+.+$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            title,
            re.IGNORECASE
        )

        if match:

            company = match.group(1).strip()

            if (
                2 <= len(company) <= 150
            ):
                return company

    # Some feeds expose company explicitly.
    if description:

        match = re.search(
            r"(?:company|employer)\s*:\s*([^\n|]+)",
            description,
            re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return None


def parse_feed(
    xml_text,
    source_name,
    source_url
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

        title = get_child_text(
            item,
            ["title"]
        )

        if not title:
            continue

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        job_url = normalize_url(
            get_link(item)
        )

        if not job_url:
            continue

        # ----------------------------------------------------
        # Description
        # ----------------------------------------------------

        description = get_child_text(
            item,
            [
                "description",
                "summary",
                "content",
                "content:encoded",
            ]
        )

        description = clean_text(
            description
        )

        # ----------------------------------------------------
        # Publication date
        # ----------------------------------------------------

        published_raw = get_child_text(
            item,
            [
                "pubDate",
                "published",
                "updated",
                "date",
                "dc:date",
            ]
        )

        published_at = parse_date(
            published_raw
        )

        # ----------------------------------------------------
        # Company
        # ----------------------------------------------------

        company = get_child_text(
            item,
            [
                "company",
                "employer",
            ]
        )

        company = clean_text(
            company
        )

        if not company:

            company = extract_company(
                title,
                description
            )

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        location = get_child_text(
            item,
            [
                "location",
                "jobLocation",
                "region",
            ]
        )

        location = clean_text(
            location
        )

        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        category = get_child_text(
            item,
            [
                "category"
            ]
        )

        category = clean_text(
            category
        )

        # ----------------------------------------------------
        # Record
        # ----------------------------------------------------

        record = {
            "schemaVersion": "1.0",
            "recordType": "job",

            "source": {
                "name": source_name,
                "url": source_url,
            },

            "content": {
                "title": title,
                "company": company,
                "description": description,
                "location": location,
                "category": category,
                "url": job_url,
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
        }

        record["content_hash"] = (
            make_content_hash(
                title,
                company,
                description
            )
        )

        records.append(
            record
        )

    return records


# ============================================================
# 24-HOUR FRESHNESS
# ============================================================

def is_fresh(
    record,
    now=None
):

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

    # Never accept future publication dates.
    if published > now:
        return False

    return (
        now - published
        <= timedelta(
            hours=MAX_AGE_HOURS
        )
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

        content_hash = record.get(
            "content_hash"
        )

        # Strongest identity: URL.
        if url and url in seen_urls:
            continue

        # Secondary identity:
        # title + company + description.
        if (
            content_hash
            and content_hash in seen_hashes
        ):
            continue

        if url:
            seen_urls.add(
                url
            )

        if content_hash:
            seen_hashes.add(
                content_hash
            )

        unique.append(
            record
        )

    return unique


# ============================================================
# FETCH
# ============================================================

async def fetch_source(
    crawler,
    source
):

    print(
        f"\nFetching {source['name']}..."
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
        f"Fetched {len(records)} jobs"
    )

    return records


# ============================================================
# SAVE
# ============================================================

def save_jobs(jobs):

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
            jobs,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 70)
    print("FRONTIER ATLAS — AI JOB COLLECTION")
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

        results = await asyncio.gather(
            *[
                fetch_source(
                    crawler,
                    source
                )
                for source in JOB_SOURCES
            ]
        )

    finally:

        await crawler.close()

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    all_jobs = []

    for records in results:

        all_jobs.extend(
            records
        )

    print(
        f"\nTotal fetched: "
        f"{len(all_jobs)}"
    )

    # --------------------------------------------------------
    # 24-hour filter
    # --------------------------------------------------------

    fresh_jobs = [
        job
        for job in all_jobs
        if is_fresh(
            job,
            now
        )
    ]

    print(
        f"Jobs within last 24 hours: "
        f"{len(fresh_jobs)}"
    )

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    unique_jobs = deduplicate(
        fresh_jobs
    )

    # Newest first.
    unique_jobs.sort(
        key=lambda job: (
            job
            .get("content", {})
            .get("published_at")
            or ""
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_jobs(
        unique_jobs
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    missing_url = sum(
        1
        for job in unique_jobs
        if not job
        .get("content", {})
        .get("url")
    )

    missing_title = sum(
        1
        for job in unique_jobs
        if not job
        .get("content", {})
        .get("title")
    )

    missing_date = sum(
        1
        for job in unique_jobs
        if not job
        .get("content", {})
        .get("published_at")
    )

    print("\n" + "=" * 70)
    print("JOB COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"Fetched: {len(all_jobs)}"
    )

    print(
        f"Fresh (<24h): "
        f"{len(fresh_jobs)}"
    )

    print(
        f"Unique: "
        f"{len(unique_jobs)}"
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

    for job in unique_jobs:

        source = (
            job
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

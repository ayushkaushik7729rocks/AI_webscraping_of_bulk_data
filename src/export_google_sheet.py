import json
import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

DATA_DIR = Path("data")

STARTUPS_FILE = DATA_DIR / "startups_1000.json"
PRODUCTS_FILE = DATA_DIR / "products_1000.json"
PAPERS_FILE = DATA_DIR / "research_papers_1000_enriched.json"
JOBS_FILE = DATA_DIR / "jobs.json"
NEWS_FILE = DATA_DIR / "news.json"

# Put your Google service-account JSON here.
# OR set GOOGLE_SERVICE_ACCOUNT_JSON in .env.
SERVICE_ACCOUNT_FILE = Path(
    os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        "service_account.json"
    )
)

# Set this in .env:
#
# GOOGLE_SHEET_ID=your_google_sheet_id
#
SPREADSHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID"
)

SHEET_NAMES = [
    "Startups",
    "Products",
    "Research Papers",
    "Jobs",
    "News",
    "Entity Mapping Log",
]


# ============================================================
# JSON
# ============================================================

def load_json(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Missing file: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"{path} must contain a JSON list."
        )

    return data


# ============================================================
# GENERAL HELPERS
# ============================================================

def get(record, *keys):

    value = record

    for key in keys:

        if not isinstance(value, dict):
            return None

        value = value.get(key)

    return value


def first_value(record, paths):

    for path in paths:

        value = get(
            record,
            *path
        )

        if value is not None and value != "":
            return value

    return None


def text(value):

    if value is None:
        return ""

    if isinstance(value, (dict, list)):

        return json.dumps(
            value,
            ensure_ascii=False
        )

    return str(value)


def records_to_rows(
    records,
    columns,
    extractor
):

    rows = [
        columns
    ]

    for record in records:

        values = extractor(record)

        rows.append(
            [
                text(
                    values.get(column)
                )
                for column in columns
            ]
        )

    return rows


# ============================================================
# STARTUPS
# ============================================================

def startup_rows(records):

    columns = [
        "name",
        "description",
        "website",
        "location",
        "industry",
        "funding",
        "source_url",
        "source",
    ]

    def extract(record):

        content = record.get(
            "content",
            record
        )

        return {
            "name": first_value(
                record,
                [
                    ("name",),
                    ("content", "name"),
                ]
            ),

            "description": first_value(
                record,
                [
                    ("description",),
                    ("content", "description"),
                ]
            ),

            "website": first_value(
                record,
                [
                    ("website",),
                    ("content", "website"),
                ]
            ),

            "location": first_value(
                record,
                [
                    ("location",),
                    ("content", "location"),
                ]
            ),

            "industry": first_value(
                record,
                [
                    ("industry",),
                    ("category",),
                    ("content", "industry"),
                    ("content", "category"),
                ]
            ),

            "funding": first_value(
                record,
                [
                    ("funding",),
                    ("content", "funding"),
                ]
            ),

            "source_url": first_value(
                record,
                [
                    ("source_url",),
                    ("source", "url"),
                    ("content", "source_url"),
                ]
            ),

            "source": first_value(
                record,
                [
                    ("source",),
                    ("source", "name"),
                ]
            ),
        }

    return records_to_rows(
        records,
        columns,
        extract
    )


# ============================================================
# PRODUCTS
# ============================================================

def product_rows(records):

    columns = [
        "name",
        "description",
        "rating",
        "source_url",
        "source",
        "category_url",
    ]

    def extract(record):

        return {
            "name": first_value(
                record,
                [
                    ("name",),
                    ("content", "name"),
                ]
            ),

            "description": first_value(
                record,
                [
                    ("description",),
                    ("content", "description"),
                ]
            ),

            "rating": first_value(
                record,
                [
                    ("rating",),
                    ("content", "rating"),
                ]
            ),

            "source_url": first_value(
                record,
                [
                    ("source_url",),
                    ("content", "url"),
                    ("source", "url"),
                ]
            ),

            "source": first_value(
                record,
                [
                    ("source",),
                    ("source", "name"),
                ]
            ),

            "category_url": first_value(
                record,
                [
                    ("category_url",),
                    ("content", "category_url"),
                ]
            ),
        }

    return records_to_rows(
        records,
        columns,
        extract
    )


# ============================================================
# RESEARCH PAPERS
# ============================================================

def research_rows(records):

    columns = [
        "title",
        "authors",
        "paper_url",
        "published_date",
        "github_url",
        "github_stars",
        "source",
    ]

    def extract(record):

        return {
            "title": first_value(
                record,
                [
                    ("title",),
                    ("content", "title"),
                ]
            ),

            "authors": first_value(
                record,
                [
                    ("authors",),
                    ("content", "authors"),
                ]
            ),

            "paper_url": first_value(
                record,
                [
                    ("paper_url",),
                    ("content", "paper_url"),
                    ("source", "url"),
                ]
            ),

            "published_date": first_value(
                record,
                [
                    ("published_date",),
                    ("content", "published_date"),
                ]
            ),

            "github_url": first_value(
                record,
                [
                    ("github_url",),
                    ("content", "github_url"),
                ]
            ),

            "github_stars": first_value(
                record,
                [
                    ("github_stars",),
                    ("content", "github_stars"),
                ]
            ),

            "source": first_value(
                record,
                [
                    ("source", "name"),
                    ("source",),
                ]
            ),
        }

    return records_to_rows(
        records,
        columns,
        extract
    )


# ============================================================
# JOBS
# ============================================================

def job_rows(records):

    columns = [
        "title",
        "company",
        "description",
        "location",
        "category",
        "url",
        "published_at",
        "source",
    ]

    def extract(record):

        return {
            "title": first_value(
                record,
                [
                    ("content", "title"),
                    ("title",),
                ]
            ),

            "company": first_value(
                record,
                [
                    ("content", "company"),
                    ("company",),
                ]
            ),

            "description": first_value(
                record,
                [
                    ("content", "description"),
                    ("description",),
                ]
            ),

            "location": first_value(
                record,
                [
                    ("content", "location"),
                    ("location",),
                ]
            ),

            "category": first_value(
                record,
                [
                    ("content", "category"),
                    ("category",),
                ]
            ),

            "url": first_value(
                record,
                [
                    ("content", "url"),
                    ("url",),
                ]
            ),

            "published_at": first_value(
                record,
                [
                    ("content", "published_at"),
                    ("published_at",),
                ]
            ),

            "source": first_value(
                record,
                [
                    ("source", "name"),
                    ("source",),
                ]
            ),
        }

    return records_to_rows(
        records,
        columns,
        extract
    )


# ============================================================
# NEWS
# ============================================================

def news_rows(records):

    columns = [
        "title",
        "description",
        "url",
        "author",
        "published_at",
        "source",
    ]

    def extract(record):

        return {
            "title": first_value(
                record,
                [
                    ("content", "title"),
                    ("title",),
                ]
            ),

            "description": first_value(
                record,
                [
                    ("content", "description"),
                    ("description",),
                ]
            ),

            "url": first_value(
                record,
                [
                    ("content", "url"),
                    ("url",),
                ]
            ),

            "author": first_value(
                record,
                [
                    ("content", "author"),
                    ("author",),
                ]
            ),

            "published_at": first_value(
                record,
                [
                    ("content", "published_at"),
                    ("published_at",),
                ]
            ),

            "source": first_value(
                record,
                [
                    ("source", "name"),
                    ("source",),
                ]
            ),
        }

    return records_to_rows(
        records,
        columns,
        extract
    )


# ============================================================
# ENTITY MAPPING LOG
# ============================================================

def entity_mapping_rows(records):

    columns = [
        "raw_name",
        "canonical_name",
        "match_method",
        "confidence",
        "source_url",
    ]

    rows = [
        columns
    ]

    for record in records:

        # Accept either a direct mapping-log record
        # or a nested mapping structure.

        mapping = record.get(
            "mapping",
            record
        )

        if not any(
            key in mapping
            for key in [
                "raw_name",
                "canonical_name",
                "match_method",
                "confidence",
            ]
        ):
            continue

        rows.append(
            [
                text(
                    mapping.get(
                        "raw_name"
                    )
                ),

                text(
                    mapping.get(
                        "canonical_name"
                    )
                ),

                text(
                    mapping.get(
                        "match_method"
                    )
                ),

                text(
                    mapping.get(
                        "confidence"
                    )
                ),

                text(
                    mapping.get(
                        "source_url"
                    )
                ),
            ]
        )

    return rows


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(
    name,
    records,
    minimum_count=None
):

    print(
        f"{name}: {len(records)} records"
    )

    if minimum_count is not None:

        if len(records) < minimum_count:

            raise ValueError(
                f"{name} has only "
                f"{len(records)} records. "
                f"Required: {minimum_count}"
            )

    missing_url = 0

    for record in records:

        url = first_value(
            record,
            [
                ("source_url",),
                ("paper_url",),
                ("content", "url"),
                ("content", "paper_url"),
                ("source", "url"),
            ]
        )

        if not url:
            missing_url += 1

    print(
        f"  Missing source URLs: "
        f"{missing_url}"
    )


# ============================================================
# GOOGLE AUTH
# ============================================================

def connect_google():

    if not SERVICE_ACCOUNT_FILE.exists():

        raise FileNotFoundError(
            "\nGoogle service-account file not found.\n"
            f"Expected: {SERVICE_ACCOUNT_FILE}\n\n"
            "Create/download your Google service-account "
            "credentials JSON and place it at that path."
        )

    if not SPREADSHEET_ID:

        raise ValueError(
            "\nGOOGLE_SHEET_ID is not set.\n"
            "Put the target Google Sheet ID in .env."
        )

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = (
        Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=scopes
        )
    )

    client = gspread.authorize(
        credentials
    )

    return client.open_by_key(
        SPREADSHEET_ID
    )


# ============================================================
# WRITE SHEET
# ============================================================

def write_tab(
    spreadsheet,
    tab_name,
    rows
):

    try:

        worksheet = spreadsheet.worksheet(
            tab_name
        )

        worksheet.clear()

    except gspread.WorksheetNotFound:

        worksheet = spreadsheet.add_worksheet(
            title=tab_name,
            rows=max(
                len(rows) + 10,
                100
            ),
            cols=max(
                len(rows[0]) + 5,
                10
            )
        )

    # Resize before writing.
    worksheet.resize(
        rows=max(
            len(rows) + 5,
            100
        ),
        cols=max(
            len(rows[0]) + 2,
            10
        )
    )

    # Upload in chunks to avoid oversized API requests.
    chunk_size = 500

    for start in range(
        0,
        len(rows),
        chunk_size
    ):

        chunk = rows[
            start:start + chunk_size
        ]

        end_row = start + len(chunk)

        worksheet.update(
            range_name=f"A{start + 1}:"
                       f"{chr(64 + len(rows[0]))}"
                       f"{end_row}",
            values=chunk,
            value_input_option="RAW"
        )

    # Freeze header.
    worksheet.freeze(
        rows=1
    )

    print(
        f"  {tab_name}: "
        f"{len(rows) - 1} records written"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FRONTIER ATLAS — FINAL GOOGLE SHEET EXPORT")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    startups = load_json(
        STARTUPS_FILE
    )

    products = load_json(
        PRODUCTS_FILE
    )

    papers = load_json(
        PAPERS_FILE
    )

    jobs = load_json(
        JOBS_FILE
    )

    news = load_json(
        NEWS_FILE
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    print("\nDATA VALIDATION")

    validate_dataset(
        "Startups",
        startups,
        minimum_count=1000
    )

    validate_dataset(
        "Products",
        products,
        minimum_count=1000
    )

    validate_dataset(
        "Research Papers",
        papers,
        minimum_count=1000
    )

    validate_dataset(
        "Jobs",
        jobs
    )

    validate_dataset(
        "News",
        news
    )

    # --------------------------------------------------------
    # Build rows
    # --------------------------------------------------------

    print("\nBUILDING TABS")

    tabs = {
        "Startups":
            startup_rows(startups),

        "Products":
            product_rows(products),

        "Research Papers":
            research_rows(papers),

        "Jobs":
            job_rows(jobs),

        "News":
            news_rows(news),

        # Mapping log is populated only when actual mapping
        # records exist. We never fabricate mappings.
        "Entity Mapping Log":
            entity_mapping_rows(
                startups
            ),
    }

    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------

    print("\nCONNECTING TO GOOGLE SHEETS")

    spreadsheet = connect_google()

    print(
        f"Spreadsheet: "
        f"{spreadsheet.title}"
    )

    # --------------------------------------------------------
    # Write exactly six tabs
    # --------------------------------------------------------

    for tab_name in SHEET_NAMES:

        write_tab(
            spreadsheet,
            tab_name,
            tabs[tab_name]
        )

    # --------------------------------------------------------
    # Remove accidental extra tabs
    # --------------------------------------------------------

    existing = spreadsheet.worksheets()

    for worksheet in existing:

        if worksheet.title not in SHEET_NAMES:

            spreadsheet.del_worksheet(
                worksheet
            )

            print(
                f"Removed extra tab: "
                f"{worksheet.title}"
            )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    final_tabs = [
        worksheet.title
        for worksheet in spreadsheet.worksheets()
    ]

    print("\n" + "=" * 70)
    print("GOOGLE SHEET EXPORT COMPLETE")
    print("=" * 70)

    print(
        "Tabs:"
    )

    for tab in final_tabs:

        print(
            f"  ✓ {tab}"
        )

    print(
        f"\nSpreadsheet URL:\n"
        f"https://docs.google.com/spreadsheets/d/"
        f"{SPREADSHEET_ID}"
    )

    print("\nRecord counts:")

    print(
        f"  Startups: "
        f"{len(startups)}"
    )

    print(
        f"  Products: "
        f"{len(products)}"
    )

    print(
        f"  Research Papers: "
        f"{len(papers)}"
    )

    print(
        f"  Jobs: "
        f"{len(jobs)}"
    )

    print(
        f"  News: "
        f"{len(news)}"
    )

    print(
        f"  Entity Mapping Log: "
        f"{len(tabs['Entity Mapping Log']) - 1}"
    )


if __name__ == "__main__":
    main()
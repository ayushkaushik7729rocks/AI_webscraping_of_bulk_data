# FrontierAtlas

> A scalable, fault-tolerant AI data ingestion and entity-resolution pipeline for discovering AI startups, products, research papers, jobs, and news from real-world web sources.

## Overview

**FrontierAtlas** is an AI/data engineering pipeline designed to collect, normalize, validate, deduplicate, enrich, and export structured information from multiple web sources.

The system focuses on **data provenance, freshness, fault tolerance, entity resolution, and scalable ingestion** rather than building a frontend dashboard.

The current pipeline produces:

* **1,000 AI startups**
* **1,000 AI products**
* **1,000 research papers**
* **GitHub repository metrics for research papers where available**
* **105 fresh AI-related job listings**
* **13 fresh AI news articles**
* Source URLs and provenance for collected records

The final structured dataset can be exported to Excel/Google Sheets for analysis and review.

---

## Key Features

### 1. Asynchronous Web Crawling

The crawler is built around Python's asynchronous I/O capabilities.

Key features include:

* `asyncio`
* `aiohttp`
* Bounded concurrency
* Request timeouts
* Retry handling
* HTTP status-aware retry logic
* Exponential backoff with jitter
* Batch fetching

The crawler avoids unbounded parallel requests and uses controlled concurrency to reduce load on source websites.

---

### 2. Multi-Source Data Collection

FrontierAtlas uses multiple sources for different data domains.

#### Startups

The startup pipeline uses publicly accessible startup directories and discovery sources.

The current dataset contains:

**1,000 accepted startup records**

Each record is validated for:

* Startup name
* Source URL
* Source provenance
* Duplicate URLs
* Required fields

---

#### Products

The product pipeline combines AI-product discovery sources including:

* Futurepedia
* Product Hunt

The current dataset contains:

**1,000 unique AI product records**

Product Hunt extraction includes structured extraction of product names and URLs.

---

#### Research Papers

Research papers are collected using research-oriented sources including:

* arXiv
* Papers with Code

The research pipeline also attempts to resolve associated GitHub repositories and enrich papers with repository-level information.

The current dataset contains:

**1,000 research papers**

Where a legitimate GitHub repository can be resolved, repository metadata such as GitHub stars can be associated with the paper.

---

#### AI News

The news pipeline uses RSS feeds from AI/news sources.

The collector:

1. Fetches RSS/Atom feeds
2. Parses article metadata
3. Extracts publication timestamps
4. Applies a strict 24-hour freshness filter
5. Normalizes URLs
6. Removes duplicates
7. Stores source provenance

Current collection:

**13 unique AI news articles published within the previous 24 hours at collection time.**

---

#### AI Jobs

The jobs pipeline uses RSS-based job sources where available.

The pipeline:

1. Fetches job feeds
2. Parses job metadata
3. Extracts publication timestamps
4. Applies the 24-hour freshness requirement
5. Deduplicates listings
6. Preserves source URLs

Current collection:

**105 unique fresh AI-related job listings.**

---

# Architecture

The overall architecture follows a staged ingestion pipeline:

```text
                 ┌──────────────────────┐
                 │      Data Sources     │
                 │                      │
                 │ Startups              │
                 │ Products              │
                 │ Research              │
                 │ News                  │
                 │ Jobs                  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Async Crawler       │
                 │                      │
                 │ aiohttp              │
                 │ concurrency limits   │
                 │ retries              │
                 │ timeouts             │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ HTML / Feed Parsing  │
                 │                      │
                 │ BeautifulSoup        │
                 │ lxml                 │
                 │ RSS / Atom parsing   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Normalization &      │
                 │ Freshness Filtering  │
                 │                      │
                 │ URL normalization    │
                 │ date extraction      │
                 │ content hashing      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Deduplication        │
                 │                      │
                 │ URL hash             │
                 │ content hash         │
                 │ canonical identity   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Entity Resolution    │
                 │                      │
                 │ normalization        │
                 │ exact matching       │
                 │ aliases              │
                 │ fuzzy matching       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Enrichment           │
                 │                      │
                 │ GitHub metadata      │
                 │ structured fields    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Validated JSON Data  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Excel / Sheets       │
                 │ Export               │
                 └──────────────────────┘
```

---

# Data Quality and Provenance

A core design principle of FrontierAtlas is:

> **Missing data is preferable to fabricated data.**

The pipeline does not intentionally invent records, URLs, publication dates, GitHub repositories, or other source information.

Every collected record is expected to preserve its source URL.

Validation checks include:

* Required fields
* Valid source URLs
* Duplicate detection
* Date validation
* Freshness validation
* Schema consistency
* GitHub repository validation
* Entity-resolution confidence
* Record-count validation

---

# Freshness Handling

News and jobs have a strict freshness requirement.

The pipeline distinguishes between:

```text
published_at
collected_at
```

These represent different concepts.

`published_at` represents when the source claims the content was published.

`collected_at` represents when FrontierAtlas retrieved the content.

For news and jobs, the collector accepts records only when their publication time falls within the required freshness window.

The date extraction strategy prioritizes structured metadata and feed timestamps before falling back to other available signals.

---

# Deduplication

Multiple sources can reference the same underlying entity or content.

FrontierAtlas therefore uses several levels of deduplication.

### URL-level deduplication

URLs are normalized before comparison.

### Content-level deduplication

Content hashes can be used to identify repeated content appearing under different URLs.

### Entity-level deduplication

Entity resolution attempts to identify records referring to the same organization or entity.

The objective is to avoid simply counting multiple URLs as independent entities.

---

# Entity Resolution

Entity resolution is used to map different representations of the same entity to a canonical representation.

The process includes:

1. Lowercasing
2. Whitespace normalization
3. Punctuation normalization
4. Legal suffix normalization
5. Alias handling
6. Exact matching
7. Fuzzy matching
8. Confidence thresholds

Low-confidence matches are not blindly merged.

The mapping process can preserve:

```text
raw_name
canonical_name
match_method
confidence
source_url
```

This makes entity-resolution decisions auditable.

---

# GitHub Enrichment

Research papers can be associated with GitHub repositories where a legitimate repository match can be established.

The GitHub client supports authenticated API access and retrieves repository metadata such as:

* Repository owner
* Repository name
* Repository URL
* Stars

GitHub data is treated as an enrichment layer rather than as a replacement for the original research-paper source.

---

# Fault Tolerance

The crawler implements retry behavior for transient failures.

Examples include:

```text
429 Too Many Requests
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
```

The retry strategy uses bounded exponential backoff and jitter.

Conceptually:

```text
attempt 1 → short delay
attempt 2 → longer delay
attempt 3 → longer delay
```

For rate limiting, `Retry-After` can be respected when provided by the server.

The system avoids treating every HTTP error as retryable.

---

# Anti-Bot and Source Strategy

The project follows a source hierarchy that prefers less fragile access mechanisms:

```text
Official API
     ↓
RSS / Atom
     ↓
Sitemap
     ↓
Normal HTTP request
     ↓
Browser automation when permitted
     ↓
Alternative source
```

The project does not attempt to bypass CAPTCHAs or defeat access-control mechanisms.

---

# Project Structure

```text
frontier-atlas-demo/
│
├── src/
│   ├── crawler/
│   │   └── base.py
│   │
│   ├── extraction/
│   │   ├── html_parser.py
│   │   ├── freshness.py
│   │   └── record.py
│   │
│   ├── llm/
│   │   └── providers/
│   │
│   ├── entity/
│   │   ├── resolver.py
│   │   └── pipeline.py
│   │
│   ├── github/
│   │   └── client.py
│   │
│   ├── startups/
│   │
│   ├── products/
│   │
│   ├── research/
│   │
│   ├── news/
│   │
│   ├── jobs/
│   │
│   ├── storage/
│   │
│   └── main.py
│
├── tests/
│
├── data/
│
├── requirements.txt
├── architecture.pdf
├── .env.example
├── .gitignore
└── README.md
```

---

# Technology Stack

| Area                  | Technology              |
| --------------------- | ----------------------- |
| Language              | Python 3.10+            |
| Async processing      | asyncio                 |
| HTTP crawling         | aiohttp                 |
| HTML parsing          | BeautifulSoup           |
| XML parsing           | lxml                    |
| Browser automation    | Playwright              |
| Date parsing          | dateparser              |
| Validation            | Pydantic                |
| Entity resolution     | RapidFuzz               |
| Data processing       | pandas                  |
| GitHub enrichment     | GitHub API              |
| Database architecture | PostgreSQL              |
| Caching / queues      | Redis                   |
| Export                | openpyxl                |
| Testing               | pytest / pytest-asyncio |

---

# Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd frontier-atlas-demo
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If Playwright browser support is required:

```bash
playwright install chromium
```

---

# Configuration

Create a local `.env` file from `.env.example`.

Example:

```text
GEMINI_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
GITHUB_TOKEN=
```

API keys and credentials should **never be committed to the repository**.

---

# Running the Pipeline

Individual collectors can be executed independently.

For example:

```bash
python src/news/run_news.py
```

```bash
python src/jobs/run_jobs.py
```

Startup collection:

```bash
python src/startups/run_startups_1000.py
```

Product collection:

```bash
python src/products/run_products_1000.py
```

Research collection:

```bash
python src/research/run_research_1000.py
```

---

# Output

The collected datasets are stored as JSON files.

Example:

```text
data/
├── startups_1000.json
├── products_1000.json
├── research_papers_1000_enriched.json
├── jobs.json
└── news.json
```

The final Excel export contains six logical datasets/tabs:

```text
Startups
Products
Research Papers
Jobs
News
Entity Mapping Log
```

---

# Testing

The project contains tests for important pipeline components including:

* Product extraction
* Product pagination
* Product collection
* Freshness/date handling
* Entity resolution
* Startup collection
* Research collection
* Checkpoint/resume behavior

Run the test suite with:

```bash
pytest
```

---

# Scalability

The current implementation demonstrates the ingestion architecture at the required dataset size while keeping the components separable for future scaling.

A larger deployment can evolve toward:

```text
Scheduler
    │
    ▼
Redis / Kafka Queue
    │
    ├──► Crawler Workers
    │
    ├──► Extraction Workers
    │
    ├──► LLM Workers
    │
    └──► Enrichment Workers
              │
              ▼
         PostgreSQL
              │
       ┌──────┴──────┐
       ▼             ▼
    Graph DB      Vector DB
```

Scaling can be achieved by increasing worker count and infrastructure capacity rather than rewriting the core extraction logic.

Important production considerations include:

* Idempotent tasks
* Deterministic record IDs
* Content hashing
* Database uniqueness constraints
* Retry queues
* Dead-letter queues
* Per-domain rate limits
* Connection pooling
* Horizontal worker scaling

---

# Design Principles

FrontierAtlas follows several engineering principles:

### Real data over fabricated completeness

A missing optional field is preferable to an incorrect value.

### Provenance first

Records should retain the URL from which their information originated.

### Deterministic processing where possible

Parsing, normalization, deduplication, freshness checks, and validation should not depend unnecessarily on an LLM.

### Bounded concurrency

The crawler avoids uncontrolled parallelism.

### Fault isolation

A failure from one source should not prevent other sources from being processed.

### Resumability

Checkpointing allows long-running collection jobs to continue without restarting from the beginning.

### Auditability

Entity mappings and source URLs provide visibility into how records were obtained and resolved.

---

# Current Dataset

| Dataset         | Records |
| --------------- | ------: |
| AI Startups     |   1,000 |
| AI Products     |   1,000 |
| Research Papers |   1,000 |
| AI Jobs         |     105 |
| AI News         |      13 |

All reported counts refer to the datasets generated during the project collection run.

News and jobs are intentionally smaller than the startup/product/paper datasets because they use a strict **previous-24-hour freshness constraint**.

---

# Limitations

This is a demonstration/MVP implementation rather than a production-scale deployment.

Current limitations include:

* Some websites restrict automated access.
* RSS feeds can become unavailable or rate-limited.
* Not every research paper has an associated GitHub repository.
* GitHub matching can require conservative confidence thresholds.
* Some sources provide incomplete metadata.
* The current deployment does not operate a full distributed queue/worker cluster.
* PostgreSQL/Redis infrastructure is represented as the scalable target architecture rather than requiring a production cloud deployment for this demo.

These limitations are intentional trade-offs for demonstrating the core engineering architecture within the project scope.

---

# Future Improvements

Potential production improvements include:

* Distributed crawling workers
* Redis/Kafka task queues
* PostgreSQL-backed persistence
* Dead-letter queues
* More source adapters
* Automated source health monitoring
* More advanced entity-resolution strategies
* Vector search
* Knowledge graph construction
* Incremental updates
* Historical change tracking
* Production observability and metrics

---

# Conclusion

FrontierAtlas demonstrates an end-to-end approach to building a reliable AI data ingestion system.

The project combines:

**asynchronous crawling + structured extraction + freshness filtering + deduplication + entity resolution + GitHub enrichment + validation + provenance + scalable architecture**

The primary goal is not simply to collect a large number of records, but to create a pipeline where collected information can be **traced, validated, deduplicated, and extended toward production-scale ingestion.**

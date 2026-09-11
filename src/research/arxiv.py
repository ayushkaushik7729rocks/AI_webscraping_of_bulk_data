import asyncio
import urllib.parse
import xml.etree.ElementTree as ET

from src.crawler.base import AsyncCrawler


class ArxivClient:

    BASE_URL = "https://export.arxiv.org/api/query"

    def __init__(self, crawler: AsyncCrawler):
        self.crawler = crawler

    async def search(
        self,
        query: str,
        start: int = 0,
        max_results: int = 5,
    ):

        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        query_string = urllib.parse.urlencode(params)

        url = f"{self.BASE_URL}?{query_string}"

        result = await self.crawler.fetch(url)

        if result["status"] != 200:
            raise RuntimeError(
                f"arXiv request failed: "
                f"{result['status']} - {result['error']}"
            )

        return self.parse_response(
            result["html"]
        )

    def parse_response(self, xml_text: str):

        root = ET.fromstring(xml_text)

        namespace = {
            "atom": "http://www.w3.org/2005/Atom"
        }

        papers = []

        for entry in root.findall(
            "atom:entry",
            namespace
        ):

            title_element = entry.find(
                "atom:title",
                namespace
            )

            published_element = entry.find(
                "atom:published",
                namespace
            )

            summary_element = entry.find(
                "atom:summary",
                namespace
            )

            id_element = entry.find(
                "atom:id",
                namespace
            )

            links = []

            for link in entry.findall(
                "atom:link",
                namespace
            ):

                href = link.get("href")

                if href:
                    links.append({
                        "href": href,
                        "rel": link.get("rel"),
                        "type": link.get("type"),
                        "title": link.get("title"),
                    })

            title = (
                title_element.text.strip()
                if title_element is not None
                else None
            )

            published_date = (
                published_element.text.strip()
                if published_element is not None
                else None
            )

            summary = (
                summary_element.text.strip()
                if summary_element is not None
                else None
            )

            paper_url = (
                id_element.text.strip()
                if id_element is not None
                else None
            )

            authors = []

            for author in entry.findall(
                "atom:author",
                namespace
            ):

                name_element = author.find(
                    "atom:name",
                    namespace
                )

                if name_element is not None:
                    authors.append(
                        name_element.text.strip()
                    )

            papers.append({
                "title": title,
                "authors": authors,
                "paper_url": paper_url,
                "published_date": published_date,
                "summary": summary,
                "links": links,

            })

        return papers
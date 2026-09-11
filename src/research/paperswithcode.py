from bs4 import BeautifulSoup


class PapersWithCodeClient:

    BASE_URL = "https://paperswithcode.com"

    def __init__(self, crawler):
        self.crawler = crawler

    async def get_paper(
        self,
        arxiv_id
    ):

        url = (
            f"{self.BASE_URL}/paper/"
            f"{arxiv_id}"
        )

        result = await self.crawler.fetch(
            url
        )

        if result["status"] != 200:
            return {
                "url": url,
                "github_urls": [],
                "error": result["error"]
            }

        github_urls = self.extract_github_urls(
            result["html"]
        )

        return {
            "url": url,
            "github_urls": github_urls,
            "error": None
        }

    # @staticmethod
    # def extract_github_urls(html):

    #     soup = BeautifulSoup(
    #     html,
    #     "lxml"
    #     )

    #     github_urls = set()

    #     for link in soup.find_all(
    #         "a",
    #         href=True
    #     ):

    #         href = link["href"].strip()

    #         if "github.com/" not in href:
    #             continue

    #         if href.startswith("//"):
    #             href = "https:" + href

    #         elif href.startswith("/"):
    #             href = (
    #              "https://paperswithcode.com"
    #               + href
    #             )

    #         parts = href.rstrip("/").split("/")

    #     # Expected repository structure:
    #     #
    #     # https://github.com/owner/repository
    #     #
    #     # ["https:", "", "github.com", "owner", "repository"]

    #         if len(parts) < 5:
    #             continue

    #         if parts[0] not in {
    #             "https:",
    #             "http:"
    #         }:
    #             continue

    #         if parts[2].lower() != "github.com":
    #             continue

    #         owner = parts[3]
    #         repository = parts[4]

    #         if not owner or not repository:
    #             continue

    #         github_url = (
    #             f"https://github.com/"
    #             f"{owner}/{repository}"
    #         )

    #         github_urls.add(github_url)

    #     return sorted(github_urls)

    @staticmethod
    def extract_github_urls(html):

        soup = BeautifulSoup(html,"lxml")

        for link in soup.find_all("a",href=True):

            href = link["href"].strip()

            if "github.com/" not in href:
                continue

            print("\n--- GITHUB LINK ---")
            print("URL:", href)
            print("Link text:", link.get_text(" ", strip=True))

            parent = link.parent

            if parent:
                print(
                    "Parent text:",
                    parent.get_text(" ", strip=True)[:500]
                )

        return []
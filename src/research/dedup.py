import re
from urllib.parse import urlparse


class ResearchPaperDeduplicator:
    """
    Creates a deterministic identity for research papers and removes duplicates.

    Primary identity:
        arXiv ID without version suffix.

    Fallback identity:
        canonicalized paper URL.
    """

    @staticmethod
    def normalize_arxiv_id(paper_url):
        """
        Convert:
            https://arxiv.org/abs/2605.12975v1
            https://arxiv.org/abs/2605.12975v2

        into the same identity:
            arxiv:2605.12975
        """
        if not paper_url:
            return None

        match = re.search(
            r"arxiv\.org/(?:abs|pdf)/([^/?#]+)",
            paper_url,
            re.IGNORECASE,
        )

        if not match:
            return None

        arxiv_id = match.group(1)

        # Remove version suffix such as v1, v2, v3
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id, flags=re.IGNORECASE)

        return f"arxiv:{arxiv_id.lower()}"

    @staticmethod
    def canonicalize_url(url):
        """
        Normalize a URL enough to use it as a deterministic fallback ID.
        """
        if not url:
            return None

        parsed = urlparse(url)

        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/")

        return f"{scheme}://{netloc}{path}"

    @classmethod
    def get_identity(cls, paper):
        """
        Return the deterministic identity for a paper.
        """
        paper_url = paper.get("paper_url", "")

        arxiv_identity = cls.normalize_arxiv_id(paper_url)

        if arxiv_identity:
            return arxiv_identity

        canonical_url = cls.canonicalize_url(paper_url)

        if canonical_url:
            return f"url:{canonical_url}"

        return None

    @classmethod
    def deduplicate(cls, papers):
        """
        Remove duplicate papers while preserving original order.

        The first occurrence of a paper is retained.
        """
        seen = set()
        unique_papers = []

        for paper in papers:
            identity = cls.get_identity(paper)

            # If we cannot determine an identity, keep the record rather
            # than accidentally deleting valid data.
            if identity is None:
                unique_papers.append(paper)
                continue

            if identity in seen:
                continue

            seen.add(identity)
            unique_papers.append(paper)

        return unique_papers
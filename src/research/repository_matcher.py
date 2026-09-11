import re

from rapidfuzz.fuzz import ratio


class RepositoryMatcher:

    def __init__(self,minimum_score=70):
        self.minimum_score = minimum_score

    def score_repository(self,paper,repository):

        score = 0
        evidence = []

        if repository.get("source") == "explicit_paper_source": 
            return { "score": 100, "evidence": [ "explicit_paper_source" ], "accepted": True }


        paper_title = self.normalize_text(
            paper.get("title", "")
        )

        repo_name = self.normalize_text(
            repository.get("name", "")
        )

        repo_description = self.normalize_text(
            repository.get("description", "")
            or ""
        )

        # ------------------------------------------------
        # 1. Exact arXiv ID match
        # ------------------------------------------------

        arxiv_id = self.extract_arxiv_id(
            paper.get("paper_url", "")
        )

        repository_text = (
            str(repository.get("name", ""))
            + " "
            + str(repository.get("description", "") or "")
        ).lower()

        if arxiv_id and arxiv_id.lower() in repository_text:

            score += 50

            evidence.append(
                "arxiv_id_match"
            )

        # ------------------------------------------------
        # 2. Repository name similarity
        # ------------------------------------------------

        if paper_title and repo_name:

            title_score = ratio(
                paper_title,
                repo_name
            )

            if title_score >= 80:

                score += 30

                evidence.append(
                    "strong_name_similarity"
                )

            elif title_score >= 60:

                score += 15

                evidence.append(
                    "moderate_name_similarity"
                )

        # ------------------------------------------------
        # 3. Title words in description
        # ------------------------------------------------

        title_words = set(
            self.get_significant_words(
                paper_title
            )
        )

        description_words = set(
            self.get_significant_words(
                repo_description
            )
        )

        if title_words:

            overlap = (
                len(
                    title_words
                    & description_words
                )
                / len(title_words)
            )

            if overlap >= 0.6:

                score += 20

                evidence.append(
                    "description_title_overlap"
                )

            elif overlap >= 0.3:

                score += 10

                evidence.append(
                    "partial_description_overlap"
                )

        return {
            "score": min(score, 100),
            "evidence": evidence,
            "accepted": score >= self.minimum_score
        }

    @staticmethod
    def normalize_text(text):

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    @staticmethod
    def get_significant_words(text):

        stop_words = {
            "the",
            "a",
            "an",
            "for",
            "and",
            "of",
            "to",
            "in",
            "on",
            "with",
            "via",
            "from",
            "using"
        }

        words = text.split()

        return [
            word
            for word in words
            if len(word) >= 3
            and word not in stop_words
        ]

    @staticmethod
    def extract_arxiv_id(paper_url):

        match = re.search(
            r"arxiv\.org/(?:abs|pdf)/"
            r"([^/?#]+?)(?:v\d+)?$",
            paper_url
        )

        if not match:
            return None

        return match.group(1)

    def select_best_repository(self,paper,repositories):

        candidates = []

        for repository in repositories:

            result = self.score_repository(
                paper,
                repository
            )

            candidates.append({
                "repository": repository,
                "score": result["score"],
                "evidence": result["evidence"],
                "accepted": result["accepted"],
            })

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        if not candidates:
            return None

        best = candidates[0]

        if not best["accepted"]:
            return None

        return best


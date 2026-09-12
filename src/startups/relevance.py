import re


class StartupRelevanceFilter:

    POSITIVE_CATEGORY_KEYWORDS = {
        "ai",
        "artificial intelligence",
        "agentic ai",
        "generative ai",
        "frontier ai",
        "conversational ai",
        "machine learning",
        "deep learning",
        "computer vision",
        "natural language processing",
        "nlp",
        "llm",
        "ai infrastructure",
        "ai platform",
        "ai agents",
        "ai website builder",
    }

    POSITIVE_DESCRIPTION_KEYWORDS = {
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "generative ai",
        "agentic ai",
        "frontier ai",
        "conversational ai",
        "computer vision",
        "natural language processing",
        "large language model",
        "large language models",
        "llm",
        "llms",
        "ai agent",
        "ai agents",
        "ai-native",
        "ai-driven",
        "ai-assisted",
        "ai-powered",
        "ai platform",
        "ai infrastructure",
        "ai gateway",
        "ai api",
        "ai capabilities",
        "ai solutions",
        "ai technology",
        "ai technologies",
        "ai system",
        "ai systems",
        "ai application",
        "ai applications",
        "ai reasoning",
        "physical ai",
        "using ai",
        "with ai",
        "powered by ai",
        "built with ai",
    }

    NEGATIVE_KEYWORDS = {
        "online gambling",
        "online betting",
        "sports betting",
        "casino",
        "gambling",
        "betting",
        "venture capital",
        "private equity",
    }

    def __init__(
        self,
        accept_threshold=40,
    ):
        self.accept_threshold = accept_threshold

    @staticmethod
    def normalize(text):
        if not text:
            return ""

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9\s-]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    @classmethod
    def contains_keyword(cls, text, keywords):

        normalized_text = cls.normalize(text)

        matches = []

        for keyword in keywords:

            normalized_keyword = cls.normalize(
                keyword
            )

            # Short tokens such as "ai" must match
            # as complete words, not substrings.
            if " " not in normalized_keyword and len(
                normalized_keyword
            ) <= 3:

                pattern = (
                    r"\b"
                    + re.escape(normalized_keyword)
                    + r"\b"
                )

                if re.search(
                    pattern,
                    normalized_text
                ):
                    matches.append(keyword)

            else:

                if normalized_keyword in normalized_text:
                    matches.append(keyword)

        return matches

    def classify(self, startup):

        category = (
            startup.get("category", "")
            or ""
        )

        description = (
            startup.get("description", "")
            or ""
        )

        combined_text = (
            f"{category} {description}"
        )

        positive_category_matches = (
            self.contains_keyword(
                category,
                self.POSITIVE_CATEGORY_KEYWORDS
            )
        )

        positive_description_matches = (
            self.contains_keyword(
                description,
                self.POSITIVE_DESCRIPTION_KEYWORDS
            )
        )

        negative_matches = (
            self.contains_keyword(
                combined_text,
                self.NEGATIVE_KEYWORDS
            )
        )

        score = 0
        evidence = []

        if negative_matches:

            score -= 100

            for keyword in negative_matches:

                evidence.append(
                    f"negative_keyword:{keyword}"
                )

        if positive_category_matches:

            score += 70

            for keyword in positive_category_matches:

                evidence.append(
                    f"category_ai_keyword:{keyword}"
                )

        if positive_description_matches:

            score += 40

            for keyword in positive_description_matches:

                evidence.append(
                    f"description_ai_keyword:{keyword}"
                )

        if negative_matches:

            decision = "REJECT"

        elif score >= self.accept_threshold:

            decision = "ACCEPT"

        else:

            decision = "REVIEW"

        return {
            "decision": decision,
            "score": score,
            "evidence": evidence,
        }

    def filter(self, startups):

        accepted = []
        rejected = []
        review = []

        for startup in startups:

            result = self.classify(
                startup
            )

            enriched_startup = dict(
                startup
            )

            enriched_startup["relevance"] = (
                result
            )

            if result["decision"] == "ACCEPT":

                accepted.append(
                    enriched_startup
                )

            elif result["decision"] == "REVIEW":

                review.append(
                    enriched_startup
                )

            else:

                rejected.append(
                    enriched_startup
                )

        return {
            "accepted": accepted,
            "review": review,
            "rejected": rejected,
        }
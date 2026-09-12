import re
from rapidfuzz.fuzz import ratio


class EntityResolver:

    LEGAL_SUFFIXES = {
        "inc",
        "incorporated",
        "corp",
        "corporation",
        "co",
        "company",
        "ltd",
        "limited",
        "llc",
        "plc",
    }

    def __init__(
        self,
        fuzzy_threshold=90,
        aliases=None
    ):
        self.fuzzy_threshold = fuzzy_threshold
        self.aliases = aliases or {}

    @classmethod
    def normalize(cls, name):
        """
        Normalize an entity name for deterministic comparison.
        """

        if not name:
            return ""

        name = name.lower()

        # Replace punctuation with spaces.
        name = re.sub(
            r"[^a-z0-9\s]",
            " ",
            name
        )

        # Normalize whitespace.
        name = re.sub(
            r"\s+",
            " ",
            name
        ).strip()

        # Remove legal suffixes.
        words = name.split()

        while (
            words
            and words[-1] in cls.LEGAL_SUFFIXES
        ):
            words.pop()

        return " ".join(words)

    def alias_match(
        self,
        raw_name
    ):
        """
        Match a raw name against configured aliases.

        aliases format:

            {
                "open ai": "OpenAI",
                "anthropik": "Anthropic"
            }
        """

        normalized_raw = self.normalize(
            raw_name
        )

        for alias, canonical_name in self.aliases.items():

            if normalized_raw == self.normalize(alias):

                return {
                    "canonical_name": canonical_name,
                    "match_method": "alias",
                    "confidence": 1.0,
                }

        return None

    def exact_match(
        self,
        raw_name,
        canonical_names
    ):
        """
        Return the canonical name if normalized
        exact matching succeeds.
        """

        normalized_raw = self.normalize(
            raw_name
        )

        for canonical_name in canonical_names:

            normalized_canonical = (
                self.normalize(
                    canonical_name
                )
            )

            if (
                normalized_raw
                == normalized_canonical
            ):

                return {
                    "canonical_name": canonical_name,
                    "match_method": "normalized_exact",
                    "confidence": 1.0,
                }

        return None

    def resolve(
        self,
        raw_name,
        canonical_names
    ):
        """
        Resolve a raw entity name against known
        canonical entities.
        """

        if not raw_name:

            return {
                "canonical_name": None,
                "match_method": "no_match",
                "confidence": 0.0,
            }

        if not canonical_names:

            return {
                "canonical_name": None,
                "match_method": "no_match",
                "confidence": 0.0,
            }

        # -------------------------------------------------
        # 1. Normalized exact match
        # -------------------------------------------------

        exact = self.exact_match(
            raw_name,
            canonical_names
        )

        if exact:
            return exact

        # -------------------------------------------------
        # 2. Alias match
        # -------------------------------------------------

        alias = self.alias_match(
            raw_name
        )

        if alias:

            # Only accept the alias if the target
            # canonical entity actually exists.
            if alias["canonical_name"] in canonical_names:
                return alias

        # -------------------------------------------------
        # 3. Fuzzy matching
        # -------------------------------------------------

        normalized_raw = self.normalize(
            raw_name
        )

        best_name = None
        best_score = 0

        for canonical_name in canonical_names:

            normalized_canonical = (
                self.normalize(
                    canonical_name
                )
            )

            score = ratio(
                normalized_raw,
                normalized_canonical
            )

            if score > best_score:

                best_score = score
                best_name = canonical_name

        # -------------------------------------------------
        # 4. Confidence threshold
        # -------------------------------------------------

        if best_score >= self.fuzzy_threshold:

            return {
                "canonical_name": best_name,
                "match_method": "fuzzy",
                "confidence": round(
                    best_score / 100,
                    4
                ),
            }

        # -------------------------------------------------
        # 5. Don't blindly merge
        # -------------------------------------------------

        return {
            "canonical_name": None,
            "match_method": "no_match",
            "confidence": round(
                best_score / 100,
                4
            ),
        }

    @staticmethod
    def create_mapping_log(
        raw_name,
        result,
        source_url
    ):
        """
        Create one Entity Mapping Log record.
        """

        return {
            "raw_name": raw_name,
            "canonical_name": result["canonical_name"],
            "match_method": result["match_method"],
            "confidence": result["confidence"],
            "source_url": source_url,
        }
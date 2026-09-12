from urllib.parse import urlparse


class StartupExtractor:

    REQUIRED_FIELDS = {
        "name",
        "source_url",
        "source",
    }

    @staticmethod
    def normalize_url(url):
        if not url:
            return None

        parsed = urlparse(url)

        if not parsed.scheme:
            return None

        if not parsed.netloc:
            return None

        return (
            f"{parsed.scheme.lower()}://"
            f"{parsed.netloc.lower()}"
            f"{parsed.path.rstrip('/')}"
        )

    @classmethod
    def validate(cls, startup):
        """
        Validate the minimum startup record.

        Missing optional information is acceptable.
        Missing provenance is not.
        """

        for field in cls.REQUIRED_FIELDS:

            value = startup.get(field)

            if not value:
                return False

        source_url = cls.normalize_url(
            startup["source_url"]
        )

        if not source_url:
            return False

        return True

    @classmethod
    def clean(cls, startup):

        cleaned = dict(startup)

        cleaned["name"] = (
            startup["name"]
            .strip()
        )

        cleaned["source_url"] = (
            cls.normalize_url(
                startup["source_url"]
            )
        )

        return cleaned
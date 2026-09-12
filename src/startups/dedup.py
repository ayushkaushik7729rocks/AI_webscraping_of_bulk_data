from src.entity.resolver import EntityResolver


class StartupDeduplicator:

    @staticmethod
    def identity(startup):
        """
        Primary identity is the normalized source URL.
        """

        source_url = startup.get(
            "source_url"
        )

        if source_url:
            return (
                "url:",
                source_url.lower().rstrip("/")
            )

        name = startup.get(
            "name",
            ""
        )

        return (
            "name:",
            EntityResolver.normalize(name)
        )

    @classmethod
    def deduplicate(cls, startups):

        seen = set()
        unique = []

        for startup in startups:

            identity = cls.identity(
                startup
            )

            if identity in seen:
                continue

            seen.add(identity)
            unique.append(startup)

        return unique
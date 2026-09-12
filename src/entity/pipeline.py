from src.entity.resolver import EntityResolver


class EntityResolutionPipeline:

    def __init__(
        self,
        canonical_names,
        aliases=None,
        fuzzy_threshold=90
    ):
        self.canonical_names = canonical_names

        self.resolver = EntityResolver(
            fuzzy_threshold=fuzzy_threshold,
            aliases=aliases
        )

    def resolve_record(
        self,
        record,
        name_field,
        source_url_field
    ):
        """
        Resolve one record.

        Returns:
            {
                "record": original record,
                "resolution": {...},
                "mapping": {...}
            }
        """

        raw_name = record.get(
            name_field,
            ""
        )

        source_url = record.get(
            source_url_field,
            ""
        )

        resolution = self.resolver.resolve(
            raw_name=raw_name,
            canonical_names=self.canonical_names
        )

        mapping = self.resolver.create_mapping_log(
            raw_name=raw_name,
            result=resolution,
            source_url=source_url
        )

        return {
            "record": record,
            "resolution": resolution,
            "mapping": mapping
        }

    def resolve_records(
        self,
        records,
        name_field,
        source_url_field
    ):
        """
        Resolve a collection of records.
        """

        results = []

        for record in records:

            result = self.resolve_record(
                record=record,
                name_field=name_field,
                source_url_field=source_url_field
            )

            results.append(result)

        return results

    @staticmethod
    def get_mapping_log(results):
        """
        Extract only mapping-log records.
        """

        return [
            result["mapping"]
            for result in results
        ]

    @staticmethod
    def get_resolved_records(results):
        """
        Return records for which a canonical
        entity was successfully resolved.
        """

        resolved = []

        for result in results:

            resolution = result["resolution"]

            if resolution["canonical_name"] is None:
                continue

            record = dict(result["record"])

            record["canonical_name"] = (
                resolution["canonical_name"]
            )

            resolved.append(record)

        return resolved
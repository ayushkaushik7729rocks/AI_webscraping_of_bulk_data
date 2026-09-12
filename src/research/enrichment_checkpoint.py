import json
from pathlib import Path


class EnrichmentCheckpoint:

    def __init__(
        self,
        file_path="data/research_enrichment_checkpoint.json"
    ):
        self.file_path = Path(file_path)

    def load(self):
        """
        Load previously enriched records.

        Returns an empty list if no checkpoint exists.
        """

        if not self.file_path.exists():
            return []

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def save(self, records):
        """
        Persist successfully enriched records.
        """

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=2,
                ensure_ascii=False
            )

    def exists(self):
        return self.file_path.exists()

    def delete(self):
        if self.file_path.exists():
            self.file_path.unlink()
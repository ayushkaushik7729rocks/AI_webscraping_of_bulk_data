import json
from pathlib import Path


class ResearchCheckpoint:

    def __init__(
        self,
        file_path="data/research_papers_checkpoint.json"
    ):
        self.file_path = Path(file_path)

    def save(
        self,
        query,
        next_start,
        papers
    ):
        """
        Save the current collection state.

        next_start is the ArXiv offset that should be used
        when the collection resumes.
        """

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        checkpoint = {
            "query": query,
            "next_start": next_start,
            "papers": papers
        }

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                checkpoint,
                file,
                indent=2,
                ensure_ascii=False
            )

    def load(self):
        """
        Load an existing checkpoint.

        Returns None when no checkpoint exists.
        """

        if not self.file_path.exists():
            return None

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def exists(self):
        return self.file_path.exists()

    def delete(self):
        """
        Delete the checkpoint after a successful
        final collection.
        """

        if self.file_path.exists():
            self.file_path.unlink()
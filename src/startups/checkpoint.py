import json
from pathlib import Path


class StartupCheckpoint:

    def __init__(self, file_path="data/startup_checkpoint.json"):
        self.file_path = Path(file_path)

    def save(self, last_completed_page, accepted, review):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        seen_urls = [
            startup["source_url"]
            for startup in accepted + review
            if startup.get("source_url")
        ]

        checkpoint = {
            "last_completed_page": last_completed_page,
            "accepted": accepted,
            "review": review,
            "seen_urls": seen_urls,
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
        if not self.file_path.exists():
            return {
                "last_completed_page": 0,
                "accepted": [],
                "review": [],
                "seen_urls": [],
            }

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:
            checkpoint = json.load(file)

        # Backward compatibility with the old checkpoint format
        if "accepted" not in checkpoint:
            startups = checkpoint.get("startups", [])

            checkpoint = {
                "last_completed_page": checkpoint.get(
                    "last_completed_page",
                    0
                ),
                "accepted": startups,
                "review": [],
                "seen_urls": checkpoint.get(
                    "seen_urls",
                    []
                ),
            }

        return checkpoint

    def exists(self):
        return self.file_path.exists()

    def delete(self):
        if self.file_path.exists():
            self.file_path.unlink()
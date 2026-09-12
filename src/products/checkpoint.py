import json
from pathlib import Path


class ProductCheckpoint:

    def __init__(
        self,
        file_path="data/product_checkpoint.json"
    ):
        self.file_path = Path(file_path)

    def save(
        self,
        last_completed_page,
        products
    ):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        seen_urls = [
            product["source_url"]
            for product in products
            if product.get("source_url")
        ]

        checkpoint = {
            "last_completed_page": last_completed_page,
            "products": products,
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
                "products": [],
                "seen_urls": [],
            }

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            checkpoint = json.load(file)

        return {
            "last_completed_page": checkpoint.get(
                "last_completed_page",
                0
            ),
            "products": checkpoint.get(
                "products",
                []
            ),
            "seen_urls": checkpoint.get(
                "seen_urls",
                []
            ),
        }

    def exists(self):
        return self.file_path.exists()

    def delete(self):

        if self.file_path.exists():
            self.file_path.unlink()    
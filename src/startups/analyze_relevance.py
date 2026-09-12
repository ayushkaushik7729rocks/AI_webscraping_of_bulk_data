import json
from collections import Counter
from pathlib import Path


INPUT_PATH = Path(
    "data/startuphub_300_filtered.json"
)


def main():

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    review = data["review"]

    print("=" * 70)
    print("REVIEW ANALYSIS")
    print("=" * 70)

    print("Review records:", len(review))

    # Count categories
    categories = Counter(
        startup.get("category")
        for startup in review
    )

    print("\nTOP CATEGORIES")
    print("-" * 70)

    for category, count in categories.most_common(30):
        print(
            f"{count:3} | {category}"
        )

    # Print all review records in a compact format
    print("\n" + "=" * 70)
    print("REVIEW RECORDS")
    print("=" * 70)

    for index, startup in enumerate(
        review,
        start=1
    ):

        print(
            f"\n[{index}] {startup.get('name')}"
        )

        print(
            f"Category: {startup.get('category')}"
        )

        print(
            f"Description: {startup.get('description')}"
        )

        print(
            f"URL: {startup.get('source_url')}"
        )


if __name__ == "__main__":
    main()
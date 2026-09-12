import json
from pathlib import Path

from src.startups.relevance import StartupRelevanceFilter


INPUT_PATH = Path("data/startuphub_300.json")
OUTPUT_PATH = Path("data/startuphub_300_filtered.json")


def main():
    # Load the collected StartupHub records
    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        startups = json.load(file)

    print("=" * 70)
    print("STARTUP RELEVANCE FILTER")
    print("=" * 70)

    print("Input records:", len(startups))

    # Create the relevance filter
    relevance_filter = StartupRelevanceFilter()

    # Classify all startups
    results = relevance_filter.filter(startups)

    accepted = results["accepted"]
    review = results["review"]
    rejected = results["rejected"]

    # Print statistics
    print("\nRESULTS")
    print("-" * 70)

    print("Accepted:", len(accepted))
    print("Review:", len(review))
    print("Rejected:", len(rejected))
    print("Total:", len(accepted) + len(review) + len(rejected))

    # Show examples
    print("\n" + "=" * 70)
    print("ACCEPTED EXAMPLES")
    print("=" * 70)

    for startup in accepted[:10]:
        print(
            f"{startup['name']} | "
            f"{startup.get('category')} | "
            f"{startup.get('description')}"
        )

    print("\n" + "=" * 70)
    print("REVIEW EXAMPLES")
    print("=" * 70)

    for startup in review[:10]:
        print(
            f"{startup['name']} | "
            f"{startup.get('category')} | "
            f"{startup.get('description')}"
        )

    print("\n" + "=" * 70)
    print("REJECTED EXAMPLES")
    print("=" * 70)

    for startup in rejected[:10]:
        print(
            f"{startup['name']} | "
            f"{startup.get('category')} | "
            f"{startup.get('description')}"
        )

    # Save filtered results
    output = {
        "accepted": accepted,
        "review": review,
        "rejected": rejected,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)
    print("SAVED")
    print("=" * 70)
    print("Output:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
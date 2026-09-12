from src.research.enrichment_checkpoint import (
    EnrichmentCheckpoint
)


def test_checkpoint_save_and_load(tmp_path):

    checkpoint_file = (
        tmp_path / "enrichment.json"
    )

    checkpoint = EnrichmentCheckpoint(
        checkpoint_file
    )

    records = [
        {
            "content": {
                "title": "Paper A",
                "paper_url": (
                    "https://arxiv.org/abs/1234.0001v1"
                )
            }
        }
    ]

    checkpoint.save(records)

    loaded = checkpoint.load()

    assert loaded == records


def test_missing_checkpoint_returns_empty_list(tmp_path):

    checkpoint_file = (
        tmp_path / "missing.json"
    )

    checkpoint = EnrichmentCheckpoint(
        checkpoint_file
    )

    assert checkpoint.load() == []


def test_checkpoint_exists_and_delete(tmp_path):

    checkpoint_file = (
        tmp_path / "enrichment.json"
    )

    checkpoint = EnrichmentCheckpoint(
        checkpoint_file
    )

    checkpoint.save([])

    assert checkpoint.exists()

    checkpoint.delete()

    assert not checkpoint.exists()
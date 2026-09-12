import json

from src.research.checkpoint import ResearchCheckpoint


def test_checkpoint_save_and_load(tmp_path):

    checkpoint_file = (
        tmp_path / "checkpoint.json"
    )

    checkpoint = ResearchCheckpoint(
        checkpoint_file
    )

    papers = [
        {
            "title": "Paper A",
            "paper_url": (
                "https://arxiv.org/abs/1234.0001v1"
            )
        }
    ]

    checkpoint.save(
        query="cat:cs.AI",
        next_start=100,
        papers=papers
    )

    loaded = checkpoint.load()

    assert loaded["query"] == "cat:cs.AI"
    assert loaded["next_start"] == 100
    assert loaded["papers"] == papers


def test_checkpoint_missing_returns_none(tmp_path):

    checkpoint_file = (
        tmp_path / "missing.json"
    )

    checkpoint = ResearchCheckpoint(
        checkpoint_file
    )

    assert checkpoint.load() is None


def test_checkpoint_delete(tmp_path):

    checkpoint_file = (
        tmp_path / "checkpoint.json"
    )

    checkpoint = ResearchCheckpoint(
        checkpoint_file
    )

    checkpoint.save(
        query="cat:cs.AI",
        next_start=100,
        papers=[]
    )

    assert checkpoint.exists()

    checkpoint.delete()

    assert not checkpoint.exists()
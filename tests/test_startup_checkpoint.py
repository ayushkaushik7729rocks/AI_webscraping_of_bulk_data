from src.startups.checkpoint import StartupCheckpoint


def test_checkpoint_save_and_load(tmp_path):

    checkpoint_path = tmp_path / "checkpoint.json"

    checkpoint = StartupCheckpoint(checkpoint_path)

    accepted = [
        {
            "name": "Company A",
            "source_url": "https://example.com/a",
        },
        {
            "name": "Company B",
            "source_url": "https://example.com/b",
        },
    ]

    review = []

    checkpoint.save(
        last_completed_page=3,
        accepted=accepted,
        review=review
    )

    result = checkpoint.load()

    assert result["last_completed_page"] == 3
    assert result["accepted"] == accepted
    assert result["review"] == review
    assert result["seen_urls"] == [
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_checkpoint_returns_empty_state_when_missing(tmp_path):

    checkpoint = StartupCheckpoint(
        tmp_path / "missing.json"
    )

    result = checkpoint.load()

    assert result["last_completed_page"] == 0
    assert result["accepted"] == []
    assert result["review"] == []
    assert result["seen_urls"] == []


def test_checkpoint_exists(tmp_path):

    checkpoint = StartupCheckpoint(
        tmp_path / "checkpoint.json"
    )

    assert checkpoint.exists() is False

    checkpoint.save(
        last_completed_page=1,
        accepted=[],
        review=[]
    )

    assert checkpoint.exists() is True


def test_checkpoint_delete(tmp_path):

    checkpoint = StartupCheckpoint(
        tmp_path / "checkpoint.json"
    )

    checkpoint.save(
        last_completed_page=1,
        accepted=[],
        review=[]
    )

    assert checkpoint.exists() is True

    checkpoint.delete()

    assert checkpoint.exists() is False


def test_checkpoint_separates_accepted_and_review(tmp_path):

    checkpoint = StartupCheckpoint(
        tmp_path / "checkpoint.json"
    )

    accepted = [
        {
            "name": "AI Company",
            "source_url": "https://example.com/ai"
        }
    ]

    review = [
        {
            "name": "Maybe AI",
            "source_url": "https://example.com/maybe"
        }
    ]

    checkpoint.save(
        last_completed_page=5,
        accepted=accepted,
        review=review
    )

    loaded = checkpoint.load()

    assert loaded["last_completed_page"] == 5
    assert loaded["accepted"] == accepted
    assert loaded["review"] == review

    assert loaded["seen_urls"] == [
        "https://example.com/ai",
        "https://example.com/maybe",
    ]
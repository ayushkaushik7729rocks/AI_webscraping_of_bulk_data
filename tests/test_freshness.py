from datetime import datetime, timezone

from src.extraction.freshness import FreshnessValidator


def test_content_within_24_hours_is_fresh():

    validator = FreshnessValidator(
        max_age_hours=24
    )

    collected_at = datetime(
        2026,
        9,
        11,
        12,
        0,
        tzinfo=timezone.utc
    )

    published_at = (
        "2026-09-11T10:00:00+00:00"
    )

    assert validator.is_fresh(
        published_at,
        collected_at
    )


def test_content_older_than_24_hours_is_not_fresh():

    validator = FreshnessValidator(
        max_age_hours=24
    )

    collected_at = datetime(
        2026,
        9,
        11,
        12,
        0,
        tzinfo=timezone.utc
    )

    published_at = (
        "2026-09-10T10:00:00+00:00"
    )

    assert not validator.is_fresh(
        published_at,
        collected_at
    )


def test_future_content_is_not_fresh():

    validator = FreshnessValidator(
        max_age_hours=24
    )

    collected_at = datetime(
        2026,
        9,
        11,
        12,
        0,
        tzinfo=timezone.utc
    )

    published_at = (
        "2026-09-11T13:00:00+00:00"
    )

    assert not validator.is_fresh(
        published_at,
        collected_at
    )


def test_missing_publication_date_is_not_fresh():

    validator = FreshnessValidator(
        max_age_hours=24
    )

    collected_at = datetime(
        2026,
        9,
        11,
        12,
        0,
        tzinfo=timezone.utc
    )

    assert not validator.is_fresh(
        None,
        collected_at
    )
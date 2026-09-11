from datetime import datetime, timedelta, timezone


class FreshnessValidator:

    def __init__(self, max_age_hours=24):
        self.max_age = timedelta(
            hours=max_age_hours
        )

    def is_fresh(
        self,
        published_at: str,
        collected_at: datetime
    ) -> bool:

        if not published_at:
            return False

        published_datetime = datetime.fromisoformat(
            published_at
        )

        # Make sure both timestamps are timezone-aware.
        if published_datetime.tzinfo is None:
            published_datetime = published_datetime.replace(
                tzinfo=timezone.utc
            )

        if collected_at.tzinfo is None:
            collected_at = collected_at.replace(
                tzinfo=timezone.utc
            )

        age = collected_at - published_datetime

        return timedelta(0) <= age <= self.max_age
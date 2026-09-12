from src.entity.pipeline import (
    EntityResolutionPipeline
)


def test_resolve_record():

    pipeline = EntityResolutionPipeline(
        canonical_names=[
            "OpenAI",
            "Anthropic"
        ]
    )

    record = {
        "name": "OpenAI Inc.",
        "website": (
            "https://example.com/openai"
        )
    }

    result = pipeline.resolve_record(
        record=record,
        name_field="name",
        source_url_field="website"
    )

    assert (
        result["resolution"]["canonical_name"]
        == "OpenAI"
    )

    assert (
        result["resolution"]["match_method"]
        == "normalized_exact"
    )

    assert (
        result["mapping"]["raw_name"]
        == "OpenAI Inc."
    )

    assert (
        result["mapping"]["canonical_name"]
        == "OpenAI"
    )


def test_resolve_multiple_records():

    pipeline = EntityResolutionPipeline(
        canonical_names=[
            "OpenAI",
            "Anthropic"
        ]
    )

    records = [
        {
            "name": "OpenAI Inc.",
            "website": "https://example.com/openai"
        },
        {
            "name": "Anthropic LLC",
            "website": (
                "https://example.com/anthropic"
            )
        }
    ]

    results = pipeline.resolve_records(
        records=records,
        name_field="name",
        source_url_field="website"
    )

    assert len(results) == 2

    assert (
        results[0]["resolution"]["canonical_name"]
        == "OpenAI"
    )

    assert (
        results[1]["resolution"]["canonical_name"]
        == "Anthropic"
    )


def test_get_mapping_log():

    pipeline = EntityResolutionPipeline(
        canonical_names=["OpenAI"]
    )

    records = [
        {
            "name": "OpenAI Inc.",
            "website": "https://example.com/openai"
        }
    ]

    results = pipeline.resolve_records(
        records=records,
        name_field="name",
        source_url_field="website"
    )

    mapping_log = (
        pipeline.get_mapping_log(results)
    )

    assert len(mapping_log) == 1

    assert mapping_log[0]["raw_name"] == (
        "OpenAI Inc."
    )

    assert mapping_log[0]["canonical_name"] == (
        "OpenAI"
    )


def test_get_resolved_records():

    pipeline = EntityResolutionPipeline(
        canonical_names=["OpenAI"]
    )

    records = [
        {
            "name": "OpenAI Inc.",
            "website": "https://example.com/openai"
        },
        {
            "name": "Unknown Company",
            "website": "https://example.com/unknown"
        }
    ]

    results = pipeline.resolve_records(
        records=records,
        name_field="name",
        source_url_field="website"
    )

    resolved = (
        pipeline.get_resolved_records(results)
    )

    assert len(resolved) == 1

    assert resolved[0]["canonical_name"] == (
        "OpenAI"
    )


def test_mapping_log_preserves_source_url():

    pipeline = EntityResolutionPipeline(
        canonical_names=["OpenAI"]
    )

    record = {
        "name": "OpenAI",
        "website": "https://openai.com"
    }

    result = pipeline.resolve_record(
        record=record,
        name_field="name",
        source_url_field="website"
    )

    assert (
        result["mapping"]["source_url"]
        == "https://openai.com"
    )
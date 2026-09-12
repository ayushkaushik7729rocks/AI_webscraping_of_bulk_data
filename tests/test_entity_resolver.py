from src.entity.resolver import EntityResolver


def test_normalize_lowercase_and_punctuation():

    assert (
        EntityResolver.normalize("OpenAI, Inc.")
        == "openai"
    )


def test_normalize_legal_suffix():

    assert (
        EntityResolver.normalize("Anthropic LLC")
        == "anthropic"
    )


def test_normalize_whitespace():

    assert (
        EntityResolver.normalize("  OpenAI   Inc  ")
        == "openai"
    )


def test_exact_match():

    resolver = EntityResolver()

    result = resolver.resolve(
        "OpenAI, Inc.",
        ["OpenAI", "Anthropic"]
    )

    assert result["canonical_name"] == "OpenAI"
    assert result["match_method"] == "normalized_exact"
    assert result["confidence"] == 1.0


def test_fuzzy_match():

    resolver = EntityResolver(
        fuzzy_threshold=80
    )

    result = resolver.resolve(
        "Anthropik",
        ["Anthropic", "OpenAI"]
    )

    assert result["canonical_name"] == "Anthropic"
    assert result["match_method"] == "fuzzy"
    assert result["confidence"] >= 0.80


def test_low_confidence_does_not_merge():

    resolver = EntityResolver(
        fuzzy_threshold=90
    )

    result = resolver.resolve(
        "Completely Different Company",
        ["OpenAI", "Anthropic"]
    )

    assert result["canonical_name"] is None
    assert result["match_method"] == "no_match"


def test_empty_name():

    resolver = EntityResolver()

    result = resolver.resolve(
        "",
        ["OpenAI"]
    )

    assert result["canonical_name"] is None
    assert result["confidence"] == 0.0


def test_empty_candidates():

    resolver = EntityResolver()

    result = resolver.resolve(
        "OpenAI",
        []
    )

    assert result["canonical_name"] is None
    assert result["confidence"] == 0.0

def test_alias_match():

    resolver = EntityResolver(
        aliases={
            "open ai": "OpenAI"
        }
    )

    result = resolver.resolve(
        "Open AI",
        ["OpenAI", "Anthropic"]
    )

    assert result["canonical_name"] == "OpenAI"
    assert result["match_method"] == "alias"
    assert result["confidence"] == 1.0


def test_alias_must_point_to_existing_entity():

    resolver = EntityResolver(
        aliases={
            "open ai": "OpenAI"
        }
    )

    result = resolver.resolve(
        "Open AI",
        ["Anthropic"]
    )

    assert result["canonical_name"] is None


def test_mapping_log():

    resolver = EntityResolver()

    result = resolver.resolve(
        "OpenAI Inc.",
        ["OpenAI"]
    )

    mapping = resolver.create_mapping_log(
        raw_name="OpenAI Inc.",
        result=result,
        source_url="https://example.com/openai"
    )

    assert mapping == {
        "raw_name": "OpenAI Inc.",
        "canonical_name": "OpenAI",
        "match_method": "normalized_exact",
        "confidence": 1.0,
        "source_url": (
            "https://example.com/openai"
        ),
    }


def test_mapping_log_for_unmatched_entity():

    resolver = EntityResolver()

    result = resolver.resolve(
        "Completely Unknown Company",
        ["OpenAI"]
    )

    mapping = resolver.create_mapping_log(
        raw_name="Completely Unknown Company",
        result=result,
        source_url="https://example.com/unknown"
    )

    assert mapping["raw_name"] == (
        "Completely Unknown Company"
    )

    assert mapping["canonical_name"] is None

    assert mapping["match_method"] == "no_match"

    assert mapping["source_url"] == (
        "https://example.com/unknown"
    )
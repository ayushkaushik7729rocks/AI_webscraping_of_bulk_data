from src.startups.relevance import StartupRelevanceFilter


def make_startup(
    name,
    category,
    description
):
    return {
        "name": name,
        "category": category,
        "location": None,
        "funding": None,
        "description": description,
        "source_url": (
            f"https://example.com/{name}"
        ),
        "source": "test",
    }


def test_ai_category_is_accepted():

    startup = make_startup(
        "Test AI",
        "AI",
        "AI platform for businesses."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert result["decision"] == "ACCEPT"
    assert result["score"] >= 50


def test_agentic_ai_is_accepted():

    startup = make_startup(
        "Test Agent",
        "Agentic AI",
        "Autonomous agents for enterprise."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert result["decision"] == "ACCEPT"


def test_ai_description_is_accepted():

    startup = make_startup(
        "Test Company",
        "Software",
        "We build machine learning systems."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert result["decision"] == "ACCEPT"


def test_gambling_is_rejected():

    startup = make_startup(
        "Test Casino",
        "Online Gaming",
        "Online casino and sports betting platform."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert result["decision"] == "REJECT"
    assert result["score"] < 0


def test_venture_capital_is_rejected():

    startup = make_startup(
        "Test Capital",
        "Venture Capital",
        "Investment firm funding technology companies."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert result["decision"] == "REJECT"


def test_ambiguous_startup_is_not_accepted():

    startup = make_startup(
        "Health Company",
        "HealthTech",
        "Healthcare technology company."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert result["decision"] != "ACCEPT"


def test_evidence_is_recorded():

    startup = make_startup(
        "Test AI",
        "AI",
        "AI-powered software."
    )

    classifier = StartupRelevanceFilter()

    result = classifier.classify(startup)

    assert len(result["evidence"]) > 0


def test_filter_separates_records():

    startups = [
        make_startup(
            "AI Company",
            "AI",
            "AI platform."
        ),
        make_startup(
            "Casino",
            "Online Gambling",
            "Casino and betting platform."
        ),
        make_startup(
            "Health Company",
            "HealthTech",
            "Healthcare technology."
        ),
    ]

    classifier = StartupRelevanceFilter()

    result = classifier.filter(startups)

    assert len(result["accepted"]) == 1
    assert len(result["rejected"]) == 1
    assert len(result["review"]) == 1

def test_ai_native_description_is_accepted():
    startup = {
        "name": "Example",
        "category": "Customer Support",
        "description": "An AI-native customer support platform.",
    }

    result = StartupRelevanceFilter().classify(startup)

    assert result["decision"] == "ACCEPT"


def test_ai_driven_description_is_accepted():
    startup = {
        "name": "Example",
        "category": "Fintech",
        "description": "An AI-driven financial planning platform.",
    }

    result = StartupRelevanceFilter().classify(startup)

    assert result["decision"] == "ACCEPT"


def test_ai_infrastructure_is_accepted():
    startup = {
        "name": "Example",
        "category": "Finance",
        "description": "On-premise AI infrastructure for regulated industries.",
    }

    result = StartupRelevanceFilter().classify(startup)

    assert result["decision"] == "ACCEPT"


def test_physical_ai_is_accepted():
    startup = {
        "name": "Example",
        "category": "Robotics",
        "description": "Building physical AI for industrial automation.",
    }

    result = StartupRelevanceFilter().classify(startup)

    assert result["decision"] == "ACCEPT"


def test_ai_is_whole_word():
    startup = {
        "name": "Example",
        "category": "Technology",
        "description": "A company focused on training.",
    }

    result = StartupRelevanceFilter().classify(startup)

    assert "category_ai_keyword:ai" not in result["evidence"]
    assert result["decision"] == "REVIEW"

VALID_INTENTS = {
    "delivery",
    "delayed_delivery",
    "refund",
    "damaged_item",
    "cancellation",
    "other",
}

VALID_URGENCIES = {"low", "medium", "high"}

EDGE_CASES = [
    {
        "message": "My order is late, and I want my money back.",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "The item arrived broken. Can I get a refund?",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "I need to cancel my order because I ordered the wrong size.",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "My package is late. Can someone tell me where it is?",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "I was charged twice for the same order.",
        "expected_intent": "refund",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "The tracking page has not updated since yesterday.",
        "expected_intent": "delivery",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "I received the wrong product instead of what I ordered.",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "Please cancel my order immediately; I placed it by mistake.",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "I don't recognize this payment on my account.",
        "expected_intent": "refund",
        "expected_urgency": "high",
        "expected_requires_human_review": True,
    },
    {
        "message": "What are your return policy and store opening hours?",
        "expected_intent": "other",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
]


def test_edge_cases_have_all_required_fields():
    required_fields = {
        "message",
        "expected_intent",
        "expected_urgency",
        "expected_requires_human_review",
    }

    for case in EDGE_CASES:
        assert required_fields.issubset(case.keys())


def test_edge_case_messages_are_nonempty_and_unique():
    messages = [case["message"].strip() for case in EDGE_CASES]

    assert all(messages)
    assert len(messages) == len(set(messages))


def test_edge_cases_use_valid_intents_and_urgencies():
    for case in EDGE_CASES:
        assert case["expected_intent"] in VALID_INTENTS
        assert case["expected_urgency"] in VALID_URGENCIES


def test_human_review_labels_are_booleans():
    for case in EDGE_CASES:
        assert type(case["expected_requires_human_review"]) is bool

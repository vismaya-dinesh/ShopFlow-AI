
# Initial evaluation examples.
# These are expected labels, not model predictions.

EVALUATION_CASES = [
    {
        "message": "Can you tell me where my order is?",
        "expected_intent": "delivery",
    },
    {
        "message": "My package is arriving later than promised.",
        "expected_intent": "delayed_delivery",
    },
    {
        "message": "I want my money back for this purchase.",
        "expected_intent": "refund",
    },
    {
        "message": "The item arrived broken.",
        "expected_intent": "damaged_item",
    },
    {
        "message": "Please cancel my order.",
        "expected_intent": "cancellation",
    },
    {
        "message": "Can you tell me your store opening hours?",
        "expected_intent": "other",
    },
]

VALID_INTENTS = {
    "delivery",
    "delayed_delivery",
    "refund",
    "damaged_item",
    "cancellation",
    "other",
}


def test_evaluation_dataset_has_all_required_intents():
    dataset_intents = {
        case["expected_intent"] for case in EVALUATION_CASES
    }

    assert dataset_intents == VALID_INTENTS


def test_evaluation_cases_have_nonempty_messages():
    for case in EVALUATION_CASES:
        assert case["message"].strip()
        assert case["expected_intent"].strip()


def test_evaluation_cases_use_only_valid_intents():
    for case in EVALUATION_CASES:
        assert case["expected_intent"] in VALID_INTENTS


def test_evaluation_dataset_has_no_duplicate_messages():
    messages = [case["message"].strip() for case in EVALUATION_CASES]

    assert len(messages) == len(set(messages))

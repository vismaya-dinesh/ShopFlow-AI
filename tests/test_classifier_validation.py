
import json
from unittest.mock import MagicMock

import pytest

import api.classifier as classifier
from api.classifier import classify_message


def mock_ollama_response(prediction):
    """Create a mock HTTP response compatible with a with statement."""
    response = MagicMock()
    response.read.return_value = json.dumps(
        {"response": json.dumps(prediction)}
    ).encode("utf-8")

    # Make the context manager return this response when entered.
    response.__enter__.return_value = response
    response.__exit__.return_value = False

    return response


@pytest.mark.parametrize(
    ("prediction", "expected_error"),
    [
        (
            {
                "intent": "complaint",
                "urgency": "low",
                "requires_human_review": False,
            },
            "invalid intent",
        ),
        (
            {
                "intent": "delivery",
                "urgency": "critical",
                "requires_human_review": False,
            },
            "invalid urgency",
        ),
        (
            {
                "intent": "delivery",
                "urgency": "low",
                "requires_human_review": "false",
            },
            "invalid human-review value",
        ),
    ],
)
def test_classifier_rejects_invalid_predictions(
    monkeypatch, prediction, expected_error
):
    response = mock_ollama_response(prediction)

    monkeypatch.setattr(
        classifier.urllib.request,
        "urlopen",
        lambda *args, **kwargs: response,
    )

    with pytest.raises(ValueError, match=expected_error):
        classify_message("Please check my order.")


def test_classifier_accepts_valid_prediction(monkeypatch):
    prediction = {
        "intent": "delivery",
        "urgency": "low",
        "requires_human_review": False,
    }

    response = mock_ollama_response(prediction)

    monkeypatch.setattr(
        classifier.urllib.request,
        "urlopen",
        lambda *args, **kwargs: response,
    )

    result = classify_message("Where is my order?")

    assert result == prediction

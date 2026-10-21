
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from api.database import initialize_database


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_existing_order():
    initialize_database()

    with TestClient(app) as client:
        response = client.get("/orders/ORD-1001")

    assert response.status_code == 200

    data = response.json()
    assert data["order_id"] == "ORD-1001"
    assert data["item_name"] == "Wireless Headphones"
    assert data["payment_status"] == "paid"


def test_unknown_order():
    with TestClient(app) as client:
        response = client.get("/orders/ORD-9999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Order not found. Verify the order reference."
    )


def test_order_response_contains_required_fields():
    with TestClient(app) as client:
        response = client.get("/orders/ORD-1002")

    assert response.status_code == 200

    data = response.json()
    required_fields = {
        "order_id",
        "customer_email",
        "item_name",
        "order_status",
        "order_date",
        "expected_delivery",
        "payment_status",
        "total_amount",
        "currency",
    }

    assert required_fields.issubset(data.keys())


def test_order_details_are_correct():
    with TestClient(app) as client:
        response = client.get("/orders/ORD-1002")

    assert response.status_code == 200

    data = response.json()
    assert data["order_id"] == "ORD-1002"
    assert data["item_name"] == "Running Shoes"
    assert data["order_status"] == "delivered"
    assert data["currency"] == "AED"
    assert data["total_amount"] == 249


def test_unknown_order_returns_404():
    with TestClient(app) as client:
        response = client.get("/orders/ORD-9999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Order not found. Verify the order reference."
    )


def test_order_id_with_invalid_format_returns_404():
    with TestClient(app) as client:
        response = client.get("/orders/INVALID123")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Order not found. Verify the order reference."
    )


def test_review_case_workflow():
    """A review case can be created, retrieved, and completed."""
    initialize_database()

    prediction = {
        "intent": "damaged_item",
        "urgency": "medium",
        "requires_human_review": True,
    }

    with TestClient(app) as client:
        # Mock the classifier so the test does not depend on Ollama.
        with patch(
            "api.main.classify_message",
            return_value=prediction,
        ):
            response = client.post(
                "/classify",
                json={"message": "The item arrived broken."},
            )

        assert response.status_code == 200
        assert response.json()["requires_human_review"] is True

        # Find the newly created pending review case.
        response = client.get("/review-cases")
        assert response.status_code == 200

        review_case = next(
            case
            for case in response.json()
            if case["customer_message"] == "The item arrived broken."
            and case["review_status"] == "pending"
        )

        review_id = review_case["review_id"]

        # Retrieve the individual case.
        response = client.get(f"/review-cases/{review_id}")
        assert response.status_code == 200
        assert response.json()["review_id"] == review_id

        # Complete the review.
        response = client.post(
            f"/review-cases/{review_id}/complete"
        )
        assert response.status_code == 200
        assert response.json()["review_status"] == "reviewed"
        assert response.json()["reviewed_at"] is not None

        # Completing the same case again must return 409.
        response = client.post(
            f"/review-cases/{review_id}/complete"
        )
        assert response.status_code == 409


def test_review_case_not_found():
    """Review endpoints return 404 for a nonexistent case."""
    with TestClient(app) as client:
        response = client.get("/review-cases/999999")
        assert response.status_code == 404

        response = client.post(
            "/review-cases/999999/complete"
        )
        assert response.status_code == 404


def test_review_analytics_endpoint():
    """Analytics endpoint returns correctly structured metrics."""
    with TestClient(app) as client:
        response = client.get("/analytics")

    assert response.status_code == 200

    data = response.json()

    assert {
        "total_cases",
        "pending_cases",
        "reviewed_cases",
        "high_urgency_cases",
        "intent_distribution",
        "status_distribution",
    }.issubset(data.keys())

    assert data["total_cases"] == (
        data["pending_cases"] + data["reviewed_cases"]
    )

    assert data["total_cases"] >= 0
    assert data["high_urgency_cases"] >= 0
    assert isinstance(data["intent_distribution"], list)
    assert isinstance(data["status_distribution"], list)

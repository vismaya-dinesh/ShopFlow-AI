
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

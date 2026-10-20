
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.database import initialize_database, get_order


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="ShopFlow AI API",
    description="Synthetic e-commerce order lookup service",
    version="0.1.0",
    lifespan=lifespan,
)


class OrderResponse(BaseModel):
    order_id: str
    customer_email: str
    item_name: str
    order_status: str
    order_date: str
    expected_delivery: str | None
    payment_status: str
    total_amount: float
    currency: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: str):
    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found. Verify the order reference.",
        )

    return order

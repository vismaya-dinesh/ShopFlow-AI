
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.database import initialize_database, get_order
from fastapi.middleware.cors import CORSMiddleware

from api.classifier import classify_message


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

class ClassificationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


class ClassificationResponse(BaseModel):
    intent: str
    urgency: str
    requires_human_review: bool

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

@app.post(
    "/classify",
    response_model=ClassificationResponse,
)
def classify_customer_message(request: ClassificationRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Customer message cannot be empty.",
        )

    try:
        return classify_message(message)
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.classifier import classify_message
from api.database import (
    initialize_database,
    get_order,
    create_review_case,
    get_review_cases,
    get_review_case,
    mark_review_case_completed,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="ShopFlow AI API",
    description="AI-assisted e-commerce support and human-review workflow",
    version="0.2.0",
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


class ReviewCaseResponse(BaseModel):
    review_id: int
    customer_message: str
    intent: str
    urgency: str
    requires_human_review: bool
    review_status: str
    created_at: str
    reviewed_at: str | None


class ReviewCompletionResponse(ReviewCaseResponse):
    pass


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
        prediction = classify_message(message)
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

    # Automatically save messages that require human review.
    if prediction["requires_human_review"]:
        create_review_case(
            customer_message=message,
            intent=prediction["intent"],
            urgency=prediction["urgency"],
        )

    return prediction


@app.get(
    "/review-cases",
    response_model=list[ReviewCaseResponse],
)
def list_review_cases():
    return get_review_cases()


@app.get(
    "/review-cases/{review_id}",
    response_model=ReviewCaseResponse,
)
def read_review_case(review_id: int):
    review_case = get_review_case(review_id)

    if review_case is None:
        raise HTTPException(
            status_code=404,
            detail="Review case not found.",
        )

    return review_case


@app.post(
    "/review-cases/{review_id}/complete",
    response_model=ReviewCompletionResponse,
)
def complete_review_case(review_id: int):
    review_case = get_review_case(review_id)

    if review_case is None:
        raise HTTPException(
            status_code=404,
            detail="Review case not found.",
        )

    if review_case["review_status"] == "reviewed":
        raise HTTPException(
            status_code=409,
            detail="This review case has already been completed.",
        )

    completed_case = mark_review_case_completed(review_id)

    if completed_case is None:
        raise HTTPException(
            status_code=409,
            detail="This review case is no longer pending.",
        )

    return completed_case

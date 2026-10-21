
import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

VALID_INTENTS = {
    "delivery",
    "delayed_delivery",
    "refund",
    "damaged_item",
    "cancellation",
    "other",
}

VALID_URGENCIES = {"low", "medium", "high"}


def classify_message(message: str) -> dict:
    """Classify a customer support message using local Ollama."""

    prompt = f"""
You are a customer support message classifier.
Do not answer the customer. Return only a valid JSON object with
exactly these keys: intent, urgency, requires_human_review.

INTENT RULES:
- delivery: general order status, tracking, shipment, expected arrival
  when no delay is reported.
- delayed_delivery: the parcel is late or the promised date has passed.
- refund: the customer wants money returned or a charge reversed.
- damaged_item: an item arrived broken, defective, or damaged.
- cancellation: the customer wants to cancel or stop an order.
- other: none of these categories applies.

URGENCY RULES:
- urgency must be exactly low, medium, or high.
- low: general questions, routine tracking, and information requests.
- medium: every delivery delay, refund request, damaged item, and
  order cancellation.
- high: only a clearly urgent situation requiring immediate attention.

HUMAN REVIEW RULES:
- requires_human_review must be the JSON boolean true or false.
- Set it to true for every damaged_item message.
- For other intents, set it to false unless the message clearly
  requires human intervention.

EXAMPLES:
"The expected delivery date has passed" means
intent=delayed_delivery, urgency=medium, requires_human_review=false.
"The item arrived broken" means
intent=damaged_item, urgency=medium, requires_human_review=true.
"Please cancel my order" means
intent=cancellation, urgency=medium, requires_human_review=false.

Classify by meaning, not only keywords.
Return JSON only, with no Markdown or extra explanation.

Customer message:
{json.dumps(message)}
"""

    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "format": "json",
        "prompt": prompt,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        prediction = json.loads(result["response"])

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as error:
        raise RuntimeError(
            "The local AI classifier could not produce a valid response. "
            "Check that Ollama is running and the model is available."
        ) from error


    intent = prediction.get("intent")
    urgency = prediction.get("urgency")
    requires_review = prediction.get("requires_human_review")

    if not isinstance(intent, str) or intent.strip().lower() not in VALID_INTENTS:
        raise ValueError("The AI returned an invalid intent.")

    if not isinstance(urgency, str) or urgency.strip().lower() not in VALID_URGENCIES:
        raise ValueError("The AI returned an invalid urgency.")

    if type(requires_review) is not bool:
        raise ValueError("The AI returned an invalid human-review value.")

    return {
        "intent": intent.strip().lower(),
        "urgency": urgency.strip().lower(),
        "requires_human_review": requires_review,
    }

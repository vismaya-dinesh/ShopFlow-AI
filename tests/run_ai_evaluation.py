
import json
import urllib.request



EVALUATION_CASES = [
    # Delivery
    {
        "message": "Can you tell me where my order is?",
        "expected_intent": "delivery",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "Has my parcel been shipped yet?",
        "expected_intent": "delivery",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "I need an update on my shipment.",
        "expected_intent": "delivery",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "When should I expect my package?",
        "expected_intent": "delivery",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "Please check the status of order ORD-1001.",
        "expected_intent": "delivery",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },

    # Delayed delivery
    {
        "message": "My package is arriving later than promised.",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "My delivery is two days late.",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "The expected delivery date has passed.",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "My parcel hasn't arrived when it was supposed to.",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "The courier missed the promised delivery date.",
        "expected_intent": "delayed_delivery",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },

    # Refund
    {
        "message": "I want my money back for this purchase.",
        "expected_intent": "refund",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "How can I get a refund?",
        "expected_intent": "refund",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "Please return the payment to my account.",
        "expected_intent": "refund",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "I would like to request a reimbursement.",
        "expected_intent": "refund",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "Can you reverse the charge for my order?",
        "expected_intent": "refund",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },

    # Damaged item
    {
        "message": "The item arrived broken.",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "My headphones have a cracked casing.",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "The product was damaged during shipping.",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "The box was crushed and the item inside is broken.",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },
    {
        "message": "My order arrived with a part missing and the device is damaged.",
        "expected_intent": "damaged_item",
        "expected_urgency": "medium",
        "expected_requires_human_review": True,
    },

    # Cancellation
    {
        "message": "Please cancel my order.",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "I no longer want this purchase; stop the order.",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "Can I cancel before it ships?",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "I placed the order by mistake. Please cancel it.",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },
    {
        "message": "I want to withdraw my order request.",
        "expected_intent": "cancellation",
        "expected_urgency": "medium",
        "expected_requires_human_review": False,
    },

    # Other
    {
        "message": "Can you tell me your store opening hours?",
        "expected_intent": "other",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "Where can I find your product catalogue?",
        "expected_intent": "other",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "Do you offer gift wrapping?",
        "expected_intent": "other",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "I need help updating my account details.",
        "expected_intent": "other",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
    {
        "message": "Thank you for your excellent customer service.",
        "expected_intent": "other",
        "expected_urgency": "low",
        "expected_requires_human_review": False,
    },
]



def classify_message(message):
    payload = {
        "model": "qwen2.5:3b",
        "stream": False,
        "format": "json",
        "prompt": (
            "You are a customer support message classifier. "
            "Do not answer the customer. Return only a valid JSON object "
            "with exactly these keys: intent, urgency, requires_human_review. "

            "INTENT RULES: "
            "delivery means a general order-status, tracking, shipment, "
            "or expected-arrival question when no delay is reported. "
            "delayed_delivery means the promised delivery date has passed, "
            "the parcel is late, or delivery is taking longer than promised. "
            "refund means the customer wants money returned, reimbursement, "
            "a payment returned to their account, or a charge reversed. "
            "damaged_item means an item arrived broken, defective, or damaged. "
            "cancellation means the customer wants to cancel or stop an order. "
            "other means none of these categories applies. "

            "URGENCY RULES: "
            "urgency must be exactly low, medium, or high. "
            "Use low for general questions, routine tracking, and non-urgent "
            "information requests. "
            "Use medium for every reported delivery delay, including a package "
            "arriving later than promised, even if the customer does not specify "
            "how late it is. Also use medium for refund requests, damaged items, "
            "and order cancellations. "
            "Use high only when the message clearly describes an urgent situation "
            "requiring immediate attention. Do not use high without clear evidence. "

            "HUMAN REVIEW RULES: "
            "requires_human_review must be the JSON boolean true or false, "
            "not a string. "
            "Set it to true for every damaged_item message. "
            "For delivery, delayed_delivery, refund, cancellation, and other, "
            "set it to false unless the message contains a clear reason for "
            "human intervention. "

            "EXAMPLES: "
            "'The expected delivery date has passed' means "
            "intent=delayed_delivery, urgency=medium, "
            "requires_human_review=false. "
            "'Please return the payment to my account' means "
            "intent=refund, urgency=medium, requires_human_review=false. "
            "'The item arrived broken' means intent=damaged_item, "
            "urgency=medium, requires_human_review=true. "
            "'Please cancel my order' means intent=cancellation, "
            "urgency=medium, requires_human_review=false. "

            "Classify by meaning, not only by keywords. "
            "Follow the rules consistently. "
            "Return JSON only, with no Markdown or extra explanation.\n"
            f"Message: {message}"
        ),
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    return json.loads(result["response"])



def main():
    results = []

    intent_correct = 0
    urgency_correct = 0
    review_correct = 0
    all_fields_correct = 0

    valid_urgencies = {"low", "medium", "high"}

    for case in EVALUATION_CASES:
        try:
            prediction = classify_message(case["message"])

            predicted_intent = str(
                prediction.get("intent", "")
            ).strip().lower()

            predicted_urgency = str(
                prediction.get("urgency", "")
            ).strip().lower()

            predicted_review = prediction.get(
                "requires_human_review"
            )

            expected_intent = case["expected_intent"]
            expected_urgency = case["expected_urgency"]
            expected_review = case["expected_requires_human_review"]

            # Validate the model's output fields.
            intent_passed = predicted_intent == expected_intent
            urgency_passed = predicted_urgency == expected_urgency
            review_passed = (
                type(predicted_review) is bool
                and predicted_review == expected_review
            )

            if predicted_urgency not in valid_urgencies:
                urgency_passed = False

            case_passed = (
                intent_passed and urgency_passed and review_passed
            )

            intent_correct += int(intent_passed)
            urgency_correct += int(urgency_passed)
            review_correct += int(review_passed)
            all_fields_correct += int(case_passed)

            result_entry = {
                "message": case["message"],
                "expected": {
                    "intent": expected_intent,
                    "urgency": expected_urgency,
                    "requires_human_review": expected_review,
                },
                "predicted": {
                    "intent": predicted_intent,
                    "urgency": predicted_urgency,
                    "requires_human_review": predicted_review,
                },
                "checks": {
                    "intent_passed": intent_passed,
                    "urgency_passed": urgency_passed,
                    "human_review_passed": review_passed,
                    "all_fields_passed": case_passed,
                },
            }

            results.append(result_entry)

            print(
                f"{'PASS' if case_passed else 'FAIL'} | "
                f"intent={predicted_intent} "
                f"({'OK' if intent_passed else 'WRONG'}) | "
                f"urgency={predicted_urgency} "
                f"({'OK' if urgency_passed else 'WRONG'}) | "
                f"human_review={predicted_review} "
                f"({'OK' if review_passed else 'WRONG'})"
            )
            print(f"     message={case['message']}")

        except Exception as error:
            results.append({
                "message": case["message"],
                "expected": {
                    "intent": case["expected_intent"],
                    "urgency": case["expected_urgency"],
                    "requires_human_review": (
                        case["expected_requires_human_review"]
                    ),
                },
                "predicted": None,
                "checks": {
                    "intent_passed": False,
                    "urgency_passed": False,
                    "human_review_passed": False,
                    "all_fields_passed": False,
                },
                "error": str(error),
            })
            print(f"ERROR | {case['message']} | {error}")

    total = len(EVALUATION_CASES)

    if total == 0:
        print("No evaluation cases found.")
        return

    intent_accuracy = intent_correct / total * 100
    urgency_accuracy = urgency_correct / total * 100
    review_accuracy = review_correct / total * 100
    overall_accuracy = all_fields_correct / total * 100

    report = {
        "model": "qwen2.5:3b",
        "total_cases": total,
        "intent": {
            "correct": intent_correct,
            "accuracy_percent": round(intent_accuracy, 2),
        },
        "urgency": {
            "correct": urgency_correct,
            "accuracy_percent": round(urgency_accuracy, 2),
        },
        "human_review": {
            "correct": review_correct,
            "accuracy_percent": round(review_accuracy, 2),
        },
        "all_fields": {
            "correct": all_fields_correct,
            "accuracy_percent": round(overall_accuracy, 2),
        },
        "results": results,
    }

    with open("ai_evaluation_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("\n--- Evaluation Summary ---")
    print(f"Intent accuracy:       {intent_correct}/{total} ({intent_accuracy:.2f}%)")
    print(f"Urgency accuracy:      {urgency_correct}/{total} ({urgency_accuracy:.2f}%)")
    print(f"Human-review accuracy: {review_correct}/{total} ({review_accuracy:.2f}%)")
    print(f"All-fields accuracy:   {all_fields_correct}/{total} ({overall_accuracy:.2f}%)")
    print("Report saved to ai_evaluation_report.json")



if __name__ == "__main__":
    main()

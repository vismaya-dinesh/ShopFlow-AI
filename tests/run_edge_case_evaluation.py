
import json
import urllib.request
from pathlib import Path

from test_ai_edge_cases import EDGE_CASES


MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"
REPORT_PATH = Path("edge_case_evaluation_report.json")


def classify_message(message):
    payload = {
        "model": MODEL,
        "stream": False,
        "format": "json",
        "prompt": (
            "Classify the customer support message. Do not answer it. "
            "Return only a JSON object with exactly these keys: "
            "intent, urgency, requires_human_review. "

            "INTENT RULES: "
            "Choose the single most important customer issue. "
            "delivery means routine order tracking, shipment status, "
            "or expected arrival when no delay is reported. "
            "delayed_delivery means the customer reports that an order "
            "is late or the promised delivery date has passed. "
            "refund means the customer asks for money back, reimbursement, "
            "or a payment reversal. "
            "damaged_item means an item is broken, defective, or the wrong "
            "product was delivered. "
            "cancellation means the customer asks to cancel or stop an order. "
            "other means none of these categories adequately describes "
            "the main issue. "

            "A message about an unrecognized or duplicate charge is a payment "
            "dispute. Since payment_dispute is not an available intent, use "
            "refund as the closest available intent. "
            "When multiple issues appear, choose the primary issue that best "
            "describes the customer's main problem. "

            "URGENCY RULES: "
            "low means a routine question or tracking request without a reported "
            "problem. "
            "medium means a delayed delivery, refund request, damaged or incorrect "
            "item, or order cancellation, even if the customer uses words such as "
            "'immediately'. "
            "high is reserved for an unrecognized or potentially unauthorized "
            "payment, or a clearly urgent safety or security risk. "
            "A duplicate charge alone is medium urgency, not high. "
            "Do not infer high urgency from emotional wording alone. "

            "HUMAN REVIEW RULES: "
            "requires_human_review must be the JSON boolean true or false. "
            "Set it to true for damaged items, incorrect items, duplicate charges, "
            "and unrecognized payments. "
            "Set it to false for ordinary cancellations, including cancellations "
            "requested immediately, unless another issue independently requires "
            "human intervention. "
            "For other messages, set it to false unless a clear reason for human "
            "intervention is present. "

            "Examples: "
            "'My order is late, and I want my money back' means "
            "intent=delayed_delivery, urgency=medium, "
            "requires_human_review=false. "
            "'The item arrived broken. Can I get a refund?' means "
            "intent=damaged_item, urgency=medium, "
            "requires_human_review=true. "
            "'I was charged twice for the same order' means "
            "intent=refund, urgency=medium, requires_human_review=true. "
            "'I don't recognize this payment on my account' means "
            "intent=refund, urgency=high, requires_human_review=true. "
            "'What are your return policy and store opening hours?' means "
            "intent=other, urgency=low, requires_human_review=false. "

            "Return valid JSON only, without Markdown or explanation.\n"
            f"Message: {message}"
        ),
    }

    request = urllib.request.Request(
        OLLAMA_URL,
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
    all_correct = 0

    total = len(EDGE_CASES)

    if total == 0:
        print("No edge cases found.")
        return

    for case in EDGE_CASES:
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

            intent_passed = (
                predicted_intent == case["expected_intent"]
            )
            urgency_passed = (
                predicted_urgency == case["expected_urgency"]
            )
            review_passed = (
                type(predicted_review) is bool
                and predicted_review
                == case["expected_requires_human_review"]
            )

            case_passed = (
                intent_passed and urgency_passed and review_passed
            )

            intent_correct += int(intent_passed)
            urgency_correct += int(urgency_passed)
            review_correct += int(review_passed)
            all_correct += int(case_passed)

            entry = {
                "message": case["message"],
                "expected": {
                    "intent": case["expected_intent"],
                    "urgency": case["expected_urgency"],
                    "requires_human_review": (
                        case["expected_requires_human_review"]
                    ),
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
            results.append(entry)

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

    report = {
        "model": MODEL,
        "total_cases": total,
        "intent_accuracy_percent": round(
            intent_correct / total * 100, 2
        ),
        "urgency_accuracy_percent": round(
            urgency_correct / total * 100, 2
        ),
        "human_review_accuracy_percent": round(
            review_correct / total * 100, 2
        ),
        "all_fields_accuracy_percent": round(
            all_correct / total * 100, 2
        ),
        "results": results,
    }

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("\n--- Edge-Case Evaluation Summary ---")
    print(f"Intent:       {intent_correct}/{total} ({intent_correct / total * 100:.2f}%)")
    print(f"Urgency:      {urgency_correct}/{total} ({urgency_correct / total * 100:.2f}%)")
    print(f"Human review: {review_correct}/{total} ({review_correct / total * 100:.2f}%)")
    print(f"All fields:   {all_correct}/{total} ({all_correct / total * 100:.2f}%)")
    print(f"Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()

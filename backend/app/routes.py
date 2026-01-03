"""API routes blueprint for the Pharmacy Agent."""

import json
import os
import sqlite3
from flask import Blueprint, Response, jsonify, request
from openai import OpenAI

from app.services import pharmacy_service, prescription_service, user_service


main = Blueprint("main", __name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
SYSTEM_PROMPT = (
    "You are a helpful pharmacy assistant. Provide factual information only. "
    "Do not give medical advice. Redirect advice requests to a healthcare professional."
)


@main.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@main.route("/api/prescriptions/validate", methods=["GET"])
def validate_prescription():
    user_id = request.args.get("user_id", "")
    med_id = request.args.get("med_id", "")
    qty = request.args.get("qty", "1")

    try:
        requested_qty = int(qty)
        item_id = prescription_service.validate_fulfillment(user_id, med_id, requested_qty)
        return jsonify({"item_id": item_id, "requested_qty": requested_qty})
    except (ValueError, PermissionError) as err:
        return jsonify({"error": str(err)}), 400
    except sqlite3.Error as err:
        return jsonify({"error": f"database error: {err}"}), 500


@main.route("/api/prescriptions/fulfill", methods=["POST"])
def fulfill_prescription():
    data = request.get_json() or {}
    user_id = data.get("user_id", "")
    med_id = data.get("med_id", "")
    qty = data.get("qty", 1)

    try:
        requested_qty = int(qty)
        prescription_service.fulfill_prescription(user_id, med_id, requested_qty)
        return jsonify({"status": "fulfilled", "quantity": requested_qty})
    except (ValueError, PermissionError) as err:
        return jsonify({"error": str(err)}), 400
    except sqlite3.Error as err:
        return jsonify({"error": f"database error: {err}"}), 500


@main.route("/api/pharmacies/restock", methods=["POST"])
def restock():
    data = request.get_json() or {}
    manager_id = data.get("manager_id", "")
    med_id = data.get("med_id", "")
    qty = data.get("qty", 0)

    try:
        requested_qty = int(qty)
        pharmacy_service.process_restock(manager_id, med_id, requested_qty)
        return jsonify({"status": "restocked", "quantity": requested_qty})
    except (ValueError, PermissionError) as err:
        return jsonify({"error": str(err)}), 400
    except sqlite3.Error as err:
        return jsonify({"error": f"database error: {err}"}), 500


@main.route("/api/users/transaction", methods=["POST"])
def user_transaction():
    data = request.get_json() or {}
    user_id = data.get("user_id", "")
    amount_raw = data.get("amount", 0)

    try:
        amount = float(amount_raw)
        user_service.process_transaction(user_id, amount)
        return jsonify({"status": "processed", "amount": amount})
    except (ValueError, PermissionError) as err:
        return jsonify({"error": str(err)}), 400
    except sqlite3.Error as err:
        return jsonify({"error": f"database error: {err}"}), 500


@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = (data.get("message", "") or "").strip()

    if not user_message:
        return jsonify({"error": "message is required"}), 400
    if not OPENAI_API_KEY or not OPENAI_MODEL or client is None:
        return jsonify({"error": "OpenAI API is not configured"}), 500

    def stream():
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                stream=True,
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {json.dumps({'token': content})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return Response(stream(), mimetype="text/event-stream")

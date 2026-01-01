"""Prescription validation and fulfillment services."""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "pharmacy.db"


def validate_fulfillment(user_id: str, med_id: str, requested_qty: int) -> str:
	"""Ensure an active prescription exists with enough remaining periods; return item id."""

	if requested_qty <= 0:
		raise ValueError("Requested quantity must be positive")

	with sqlite3.connect(DB_PATH) as conn:
		conn.execute("PRAGMA foreign_keys = ON;")
		cursor = conn.cursor()

		cursor.execute(
			"""
			SELECT pi.id, pi.remaining_periods
			FROM prescriptions p
			JOIN prescription_items pi ON pi.prescription_id = p.id
			WHERE p.user_id = ? AND pi.med_id = ? AND p.is_active = 1;
			""",
			(user_id, med_id),
		)
		row = cursor.fetchone()

		if not row:
			raise ValueError("No active prescription found for this medication")

		item_id, remaining_periods = row

		if remaining_periods < requested_qty:
			raise ValueError("Not enough remaining periods for requested quantity")

		return item_id


def fulfill_prescription(user_id: str, med_id: str, quantity: int) -> None:
	"""Decrement prescription periods and medication stock after validation."""

	item_id = validate_fulfillment(user_id, med_id, quantity)

	with sqlite3.connect(DB_PATH) as conn:
		conn.execute("PRAGMA foreign_keys = ON;")
		cursor = conn.cursor()

		cursor.execute(
			"SELECT remaining_periods FROM prescription_items WHERE id = ?;",
			(item_id,),
		)
		remaining_row = cursor.fetchone()
		if not remaining_row or remaining_row[0] < quantity:
			raise ValueError("Not enough remaining periods to fulfill request")

		cursor.execute(
			"SELECT stock_quantity FROM medications WHERE id = ?;",
			(med_id,),
		)
		stock_row = cursor.fetchone()
		if not stock_row:
			raise ValueError("Medication not found during fulfillment")
		if stock_row[0] < quantity:
			raise ValueError("Insufficient stock to fulfill prescription")

		cursor.execute(
			"UPDATE prescription_items SET remaining_periods = remaining_periods - ? WHERE id = ?;",
			(quantity, item_id),
		)
		cursor.execute(
			"UPDATE medications SET stock_quantity = stock_quantity - ? WHERE id = ?;",
			(quantity, med_id),
		)

		cursor.execute(
			"SELECT prescription_id FROM prescription_items WHERE id = ?;",
			(item_id,),
		)
		presc_row = cursor.fetchone()
		if presc_row:
			prescription_id = presc_row[0]

			cursor.execute(
				"""
				SELECT COUNT(*)
				FROM prescription_items
				WHERE prescription_id = ? AND remaining_periods > 0;
				""",
				(prescription_id,),
			)
			remaining_count = cursor.fetchone()[0]

			if remaining_count == 0:
				cursor.execute(
					"UPDATE prescriptions SET is_active = 0 WHERE id = ?;",
					(prescription_id,),
				)

		conn.commit()

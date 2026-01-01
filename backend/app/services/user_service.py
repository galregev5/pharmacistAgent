"""User-related financial transactions."""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "pharmacy.db"


def process_transaction(user_id: str, amount: float) -> None:
	"""Increase user debt and add revenue and budget for the pharmacy."""

	with sqlite3.connect(DB_PATH) as conn:
		conn.execute("PRAGMA foreign_keys = ON;")
		cursor = conn.cursor()

		cursor.execute("SELECT debt FROM users WHERE id = ?;", (user_id,))
		user_row = cursor.fetchone()
		if not user_row:
			raise ValueError("User not found")

		cursor.execute(
			"UPDATE users SET debt = debt + ? WHERE id = ?;",
			(amount, user_id),
		)
		cursor.execute(
			"""
			UPDATE pharmacy_financials
			SET total_revenue = total_revenue + ?,
				total_budget = total_budget + ?
			WHERE id = 1;
			""",
			(amount, amount),
		)

		conn.commit()

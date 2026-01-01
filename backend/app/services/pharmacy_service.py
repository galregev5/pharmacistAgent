"""Service for inventory restocking with budget enforcement."""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "pharmacy.db"


def process_restock(user_id: str, med_id: str, qty: int) -> None:
	"""Restock medication if user is a manager and budget allows."""

	if qty <= 0:
		raise ValueError("Quantity must be positive")

	with sqlite3.connect(DB_PATH) as conn:
		conn.execute("PRAGMA foreign_keys = ON;")
		cursor = conn.cursor()

		cursor.execute("SELECT role FROM users WHERE id = ?;", (user_id,))
		role_row = cursor.fetchone()
		if not role_row:
			raise ValueError("User not found")
		if role_row[0] != "manager":
			raise PermissionError("Only managers can restock inventory")

		cursor.execute(
			"SELECT wholesale_price, stock_quantity FROM medications WHERE id = ?;",
			(med_id,),
		)
		med_row = cursor.fetchone()
		if not med_row:
			raise ValueError("Medication not found")

		wholesale_price, current_stock = med_row
		total_cost = wholesale_price * qty

		cursor.execute("SELECT total_budget FROM pharmacy_financials WHERE id = 1;")
		budget_row = cursor.fetchone()
		if not budget_row:
			raise ValueError("Pharmacy financials not initialized")

		if budget_row[0] < total_cost:
			raise ValueError("Insufficient budget to restock")

		cursor.execute(
			"UPDATE medications SET stock_quantity = stock_quantity + ? WHERE id = ?;",
			(qty, med_id),
		)
		cursor.execute(
			"UPDATE pharmacy_financials SET total_budget = total_budget - ? WHERE id = 1;",
			(total_cost,),
		)

		conn.commit()

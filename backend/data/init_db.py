"""SQLite schema and seed data initializer for the Pharmacy Agent."""

import os
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).resolve().with_name("pharmacy.db")


def initialize_database() -> None:
	"""Create a fresh database with schema and seed data."""

	if DB_PATH.exists():
		last_error = None
		for _ in range(3):
			try:
				DB_PATH.unlink()
				last_error = None
				break
			except PermissionError as exc:
				last_error = exc
				time.sleep(0.1)
		if last_error:
			raise last_error

	DB_PATH.parent.mkdir(parents=True, exist_ok=True)

	with closing(sqlite3.connect(DB_PATH)) as conn:
		conn.execute("PRAGMA foreign_keys = ON;")
		with conn:
			_create_tables(conn)
			_seed_data(conn)


def _create_tables(conn: sqlite3.Connection) -> None:
	cursor = conn.cursor()

	cursor.execute(
		"""
		CREATE TABLE users (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			role TEXT NOT NULL CHECK (role IN ('customer', 'manager', 'doctor')),
			debt REAL NOT NULL DEFAULT 0,
			created_at TEXT NOT NULL
		);
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE medications (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			active_ingredient TEXT NOT NULL,
			category TEXT NOT NULL,
			dosage_instructions TEXT NOT NULL,
			stock_quantity INTEGER NOT NULL DEFAULT 0,
			requires_prescription INTEGER NOT NULL CHECK (requires_prescription IN (0, 1)),
			retail_price REAL NOT NULL,
			wholesale_price REAL NOT NULL
		);
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE pharmacy_financials (
			id INTEGER PRIMARY KEY,
			total_budget REAL NOT NULL,
			total_revenue REAL NOT NULL
		);
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE prescriptions (
			id TEXT PRIMARY KEY,
			user_id TEXT NOT NULL,
			doctor_id TEXT NOT NULL,
			issued_date TEXT NOT NULL,
			is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
			FOREIGN KEY (user_id) REFERENCES users(id),
			FOREIGN KEY (doctor_id) REFERENCES users(id)
		);
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE prescription_items (
			id TEXT PRIMARY KEY,
			prescription_id TEXT NOT NULL,
			med_id TEXT NOT NULL,
			initial_periods INTEGER NOT NULL,
			remaining_periods INTEGER NOT NULL,
			FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
			FOREIGN KEY (med_id) REFERENCES medications(id)
		);
		"""
	)

	cursor.execute(
		"""
		CREATE TABLE interactions (
			id TEXT PRIMARY KEY,
			med_1_id TEXT NOT NULL,
			med_2_id TEXT NOT NULL,
			severity TEXT NOT NULL,
			description TEXT NOT NULL,
			FOREIGN KEY (med_1_id) REFERENCES medications(id),
			FOREIGN KEY (med_2_id) REFERENCES medications(id)
		);
		"""
	)


def _seed_data(conn: sqlite3.Connection) -> None:
	cursor = conn.cursor()
	now = datetime.now(timezone.utc).isoformat()

	users = [
		("User_Gal", "User Gal", "customer", 0.0, now),
		("User_Manager", "User Manager", "manager", 0.0, now),
		("Dr_Smith", "Dr. Smith", "doctor", 0.0, now),
	]

	medications = [
		(
			"med_acamol",
			"Acamol",
			"Paracetamol",
			"Analgesic",
			"Take 1 tablet every 6 hours as needed",
			10,
			0,
			10.0,
			5.0,
		),
		(
			"med_ritalin",
			"Ritalin",
			"Methylphenidate",
			"CNS Stimulant",
			"Take as prescribed by doctor",
			20,
			1,
			50.0,
			30.0,
		),
	]

	prescriptions = [
		("rx_user_gal_001", "User_Gal", "Dr_Smith", now, 1),
	]

	prescription_items = [
		("rx_item_user_gal_ritalin", "rx_user_gal_001", "med_ritalin", 3, 3),
	]

	pharmacy_financials = [(1, 10000.0, 0.0)]

	cursor.executemany(
		"INSERT INTO users (id, name, role, debt, created_at) VALUES (?, ?, ?, ?, ?);",
		users,
	)
	cursor.executemany(
		"""
		INSERT INTO medications (
			id, name, active_ingredient, category, dosage_instructions,
			stock_quantity, requires_prescription, retail_price, wholesale_price
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
		""",
		medications,
	)
	cursor.executemany(
		"INSERT INTO pharmacy_financials (id, total_budget, total_revenue) VALUES (?, ?, ?);",
		pharmacy_financials,
	)
	cursor.executemany(
		"INSERT INTO prescriptions (id, user_id, doctor_id, issued_date, is_active) VALUES (?, ?, ?, ?, ?);",
		prescriptions,
	)
	cursor.executemany(
		"""
		INSERT INTO prescription_items (
			id, prescription_id, med_id, initial_periods, remaining_periods
		) VALUES (?, ?, ?, ?, ?);
		""",
		prescription_items,
	)

	conn.commit()


if __name__ == "__main__":
	initialize_database()

"""Integration flow tests for pharmacy services using a real SQLite DB (fresh per test)."""

import contextlib
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.data import init_db
from backend.app.services import pharmacy_service, prescription_service, user_service

DB_PATH = ROOT_DIR / "backend" / "data" / "pharmacy.db"


def _query_single_value(query: str, params: tuple) -> float:
    with contextlib.closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row[0] if row else None


def _exec(query: str, params: tuple) -> None:
    with contextlib.closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        with conn:
            cursor = conn.cursor()
            cursor.execute(query, params)


class IntegrationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        init_db.initialize_database()

    def test_bulk_refill_flow_and_bankruptcy_guard(self):
        user_id = "User_Gal"
        med_id = "med_ritalin"
        manager_id = "User_Manager"
        acamol_id = "med_acamol"

        budget_initial = _query_single_value(
            "SELECT total_budget FROM pharmacy_financials WHERE id = 1;",
            (),
        )

        # Transaction 1: partial fill (2 of 3)
        qty_first = 2
        item_id = prescription_service.validate_fulfillment(user_id, med_id, qty_first)
        prescription_service.fulfill_prescription(user_id, med_id, qty_first)

        retail_price = _query_single_value(
            "SELECT retail_price FROM medications WHERE id = ?;", (med_id,)
        )
        amount_due_first = retail_price * qty_first if retail_price is not None else 0.0
        user_service.process_transaction(user_id, amount_due_first)

        remaining_after_first = _query_single_value(
            "SELECT remaining_periods FROM prescription_items WHERE id = ?;", (item_id,)
        )
        is_active_after_first = _query_single_value(
            "SELECT is_active FROM prescriptions WHERE id = (SELECT prescription_id FROM prescription_items WHERE id = ?);",
            (item_id,),
        )

        self.assertEqual(remaining_after_first, 1)
        self.assertTrue(bool(is_active_after_first))

        # Transaction 2: final fill (remaining 1)
        qty_second = 1
        prescription_service.validate_fulfillment(user_id, med_id, qty_second)
        prescription_service.fulfill_prescription(user_id, med_id, qty_second)

        amount_due_second = retail_price * qty_second if retail_price is not None else 0.0
        user_service.process_transaction(user_id, amount_due_second)

        remaining_after_second = _query_single_value(
            "SELECT remaining_periods FROM prescription_items WHERE id = ?;", (item_id,)
        )
        is_active_after_second = _query_single_value(
            "SELECT is_active FROM prescriptions WHERE id = (SELECT prescription_id FROM prescription_items WHERE id = ?);",
            (item_id,),
        )
        user_debt = _query_single_value(
            "SELECT debt FROM users WHERE id = ?;", (user_id,)
        )
        stock_ritalin = _query_single_value(
            "SELECT stock_quantity FROM medications WHERE id = ?;", (med_id,)
        )

        budget_after_sales = _query_single_value(
            "SELECT total_budget FROM pharmacy_financials WHERE id = 1;",
            (),
        )
        expected_budget_after_sales = budget_initial + 150.0

        self.assertEqual(remaining_after_second, 0)
        self.assertFalse(bool(is_active_after_second))
        self.assertEqual(user_debt, 150.0)
        self.assertEqual(stock_ritalin, 17)
        self.assertEqual(budget_after_sales, expected_budget_after_sales)

        # Transaction 3: manager restock for Acamol
        restock_qty = 100
        budget_before_restock = budget_after_sales
        stock_acamol_before = _query_single_value(
            "SELECT stock_quantity FROM medications WHERE id = ?;", (acamol_id,)
        )

        pharmacy_service.process_restock(manager_id, acamol_id, restock_qty)

        budget_after_restock = _query_single_value(
            "SELECT total_budget FROM pharmacy_financials WHERE id = 1;", ()
        )
        stock_acamol_after = _query_single_value(
            "SELECT stock_quantity FROM medications WHERE id = ?;", (acamol_id,)
        )

        expected_budget_after_restock = budget_before_restock - (restock_qty * 5.0)
        expected_stock_after = stock_acamol_before + restock_qty

        self.assertEqual(budget_after_restock, expected_budget_after_restock)
        self.assertEqual(stock_acamol_after, expected_stock_after)

        # Transaction 4: manager bankruptcy test (oversized order)
        bankruptcy_order_qty = 1_000_000  # would cost $5,000,000
        self.assertRaises(
            ValueError,
            pharmacy_service.process_restock,
            manager_id,
            acamol_id,
            bankruptcy_order_qty,
        )

    def test_insufficient_stock_failure(self):
        user_id = "User_Gal"
        med_id = "med_ritalin"

        # Force stock to zero to trigger insufficient stock
        _exec("UPDATE medications SET stock_quantity = 0 WHERE id = ?;", (med_id,))

        with self.assertRaises(ValueError):
            prescription_service.fulfill_prescription(user_id, med_id, 1)

    def test_unauthorized_restock(self):
        # Use non-manager user
        with self.assertRaises(PermissionError):
            pharmacy_service.process_restock("User_Gal", "med_acamol", 1)

    def test_expired_prescription(self):
        user_id = "User_Gal"
        med_id = "med_ritalin"

        # Expire the existing prescription
        _exec("UPDATE prescriptions SET is_active = 0 WHERE id = ?;", ("rx_user_gal_001",))

        with self.assertRaises(ValueError):
            prescription_service.validate_fulfillment(user_id, med_id, 1)

    def test_quota_exceeded_failure(self):
        user_id = "User_Gal"
        med_id = "med_ritalin"

        # Attempt to fulfill more than remaining periods (remaining=3 at fresh init)
        with self.assertRaises(ValueError):
            prescription_service.validate_fulfillment(user_id, med_id, 5)

    def test_wrong_medication_failure(self):
        user_id = "User_Gal"
        med_id = "med_acamol"  # No prescription for this med

        with self.assertRaises(ValueError):
            prescription_service.validate_fulfillment(user_id, med_id, 1)

    def test_non_existent_user_failure(self):
        user_id = "User_Ghost"
        med_id = "med_ritalin"

        with self.assertRaises(ValueError):
            prescription_service.validate_fulfillment(user_id, med_id, 1)


if __name__ == "__main__":
    unittest.main()

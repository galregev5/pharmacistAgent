"""Verification script for Phase 2 bulk refill flow."""

import sqlite3
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.data import init_db
from backend.app.services import pharmacy_service, prescription_service, user_service


DB_PATH = ROOT_DIR / "backend" / "data" / "pharmacy.db"


def _query_single_value(query: str, params: tuple) -> float:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row[0] if row else None


def run_scenario() -> None:
    # Initialize database
    init_db.initialize_database()

    user_id = "User_Gal"
    med_id = "med_ritalin"

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

    # Transaction 3: manager restock for Acamol
    manager_id = "User_Manager"
    acamol_id = "med_acamol"
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

    # Transaction 4: manager bankruptcy test (oversized order)
    bankruptcy_order_qty = 1_000_000  # would cost $5,000,000
    budget_before_bankruptcy = budget_after_restock

    try:
        pharmacy_service.process_restock(manager_id, acamol_id, bankruptcy_order_qty)
    except ValueError as err:
        print(f"Caught expected bankruptcy error: {err}")
    else:
        print("ERROR: Expected ValueError for bankruptcy test, but none was raised.")

    budget_after_bankruptcy = _query_single_value(
        "SELECT total_budget FROM pharmacy_financials WHERE id = 1;",
        (),
    )

    print("After first transaction (partial fill):")
    print(f"  Remaining periods: {remaining_after_first}")
    print(f"  Prescription active: {bool(is_active_after_first)}")

    print("After second transaction (final fill):")
    print(f"  Remaining periods: {remaining_after_second}")
    print(f"  Prescription active: {bool(is_active_after_second)}")

    print("Budget checks after sales:")
    print(f"  Budget initial: {budget_initial}")
    print(f"  Budget after sales: {budget_after_sales} (expected {expected_budget_after_sales})")
    print(f"  Increased as expected: {budget_after_sales > budget_initial}")

    print("Manager restock (Acamol):")
    print(f"  Budget before restock: {budget_before_restock}")
    print(f"  Budget after restock: {budget_after_restock} (expected {expected_budget_after_restock})")
    print(f"  Stock before: {stock_acamol_before}")
    print(f"  Stock after: {stock_acamol_after} (expected {expected_stock_after})")

    print("Bankruptcy safety check:")
    print(f"  Budget before oversized order: {budget_before_bankruptcy}")
    print(f"  Budget after oversized order: {budget_after_bankruptcy} (should be unchanged)")

    print("Final aggregates:")
    print(f"  User Debt: {user_debt}")
    print(f"  Ritalin Stock: {stock_ritalin}")


if __name__ == "__main__":
    run_scenario()

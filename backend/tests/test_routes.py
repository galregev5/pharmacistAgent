"""Route layer tests using Flask test client with mocked services."""

import sqlite3
import unittest
from unittest.mock import patch

from app import create_app


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health_check(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "ok"})

    @patch("app.routes.prescription_service.validate_fulfillment")
    def test_validate_prescription_success(self, mock_validate):
        mock_validate.return_value = "item123"
        resp = self.client.get("/api/prescriptions/validate", query_string={"user_id": "U1", "med_id": "M1", "qty": 2})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"item_id": "item123", "requested_qty": 2})
        mock_validate.assert_called_once_with("U1", "M1", 2)

    @patch("app.routes.prescription_service.validate_fulfillment")
    def test_validate_prescription_value_error(self, mock_validate):
        mock_validate.side_effect = ValueError("invalid")
        resp = self.client.get("/api/prescriptions/validate", query_string={"user_id": "U1", "med_id": "M1", "qty": 2})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.prescription_service.validate_fulfillment")
    def test_validate_prescription_sql_error(self, mock_validate):
        mock_validate.side_effect = sqlite3.Error("db fail")
        resp = self.client.get("/api/prescriptions/validate", query_string={"user_id": "U1", "med_id": "M1", "qty": 2})
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.pharmacy_service.process_restock")
    def test_restock_post(self, mock_restock):
        payload = {"manager_id": "User_Manager", "med_id": "med_acamol", "qty": 5}
        resp = self.client.post("/api/pharmacies/restock", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "restocked", "quantity": 5})
        mock_restock.assert_called_once_with("User_Manager", "med_acamol", 5)

    @patch("app.routes.pharmacy_service.process_restock")
    def test_restock_post_value_error(self, mock_restock):
        mock_restock.side_effect = ValueError("Invalid qty")
        payload = {"manager_id": "User_Manager", "med_id": "med_acamol", "qty": 5}
        resp = self.client.post("/api/pharmacies/restock", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.pharmacy_service.process_restock")
    def test_restock_post_sql_error(self, mock_restock):
        mock_restock.side_effect = sqlite3.Error("db fail")
        payload = {"manager_id": "User_Manager", "med_id": "med_acamol", "qty": 5}
        resp = self.client.post("/api/pharmacies/restock", json=payload)
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.pharmacy_service.process_restock")
    def test_restock_missing_keys(self, mock_restock):
        mock_restock.side_effect = ValueError("missing data")
        resp = self.client.post("/api/pharmacies/restock", json={})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())
        mock_restock.assert_called_once_with("", "", 0)

    @patch("app.routes.prescription_service.fulfill_prescription")
    def test_fulfill_post(self, mock_fulfill):
        payload = {"user_id": "User_Gal", "med_id": "med_ritalin", "qty": 2}
        resp = self.client.post("/api/prescriptions/fulfill", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "fulfilled", "quantity": 2})
        mock_fulfill.assert_called_once_with("User_Gal", "med_ritalin", 2)

    @patch("app.routes.prescription_service.fulfill_prescription")
    def test_fulfill_post_value_error(self, mock_fulfill):
        mock_fulfill.side_effect = PermissionError("not allowed")
        payload = {"user_id": "User_Gal", "med_id": "med_ritalin", "qty": 2}
        resp = self.client.post("/api/prescriptions/fulfill", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.prescription_service.fulfill_prescription")
    def test_fulfill_post_sql_error(self, mock_fulfill):
        mock_fulfill.side_effect = sqlite3.Error("db fail")
        payload = {"user_id": "User_Gal", "med_id": "med_ritalin", "qty": 2}
        resp = self.client.post("/api/prescriptions/fulfill", json=payload)
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.prescription_service.fulfill_prescription")
    def test_fulfill_invalid_qty_type(self, mock_fulfill):
        payload = {"user_id": "User_Gal", "med_id": "med_ritalin", "qty": "abc"}
        resp = self.client.post("/api/prescriptions/fulfill", json=payload)
        self.assertEqual(resp.status_code, 400)
        mock_fulfill.assert_not_called()

    @patch("app.routes.user_service.process_transaction")
    def test_user_transaction_success(self, mock_txn):
        payload = {"user_id": "User_Gal", "amount": 12.5}
        resp = self.client.post("/api/users/transaction", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "processed", "amount": 12.5})
        mock_txn.assert_called_once_with("User_Gal", 12.5)

    @patch("app.routes.user_service.process_transaction")
    def test_user_transaction_value_error(self, mock_txn):
        mock_txn.side_effect = ValueError("bad amount")
        payload = {"user_id": "User_Gal", "amount": 12.5}
        resp = self.client.post("/api/users/transaction", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.user_service.process_transaction")
    def test_user_transaction_sql_error(self, mock_txn):
        mock_txn.side_effect = sqlite3.Error("db fail")
        payload = {"user_id": "User_Gal", "amount": 12.5}
        resp = self.client.post("/api/users/transaction", json=payload)
        self.assertEqual(resp.status_code, 500)
        self.assertIn("error", resp.get_json())

    @patch("app.routes.user_service.process_transaction")
    def test_user_transaction_bad_amount(self, mock_txn):
        payload = {"user_id": "User_Gal", "amount": "lots"}
        resp = self.client.post("/api/users/transaction", json=payload)
        self.assertEqual(resp.status_code, 400)
        mock_txn.assert_not_called()


if __name__ == "__main__":
    unittest.main()

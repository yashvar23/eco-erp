# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

from __future__ import annotations
from typing import Any

import frappe
from frappe.tests.utils import FrappeTestCase


def get_test_company() -> str:
    """Resolve company for ECO test records."""
    company = frappe.defaults.get_user_default("Company")
    if company:
        return company

    first_company = frappe.get_all("Company", pluck="name", limit=1)
    return first_company[0] if first_company else ""


def assign_role(user: str, role: str) -> None:
    """Assign a role to a user for test setup if not already present."""
    if not frappe.db.exists("Has Role", {"parent": user, "role": role}):
        has_role = frappe.get_doc(
            {
                "doctype": "Has Role",
                "parent": user,
                "parenttype": "User",
                "parentfield": "roles",
                "role": role,
            }
        )
        has_role.insert(ignore_permissions=True)


def get_student_test_data(**overrides: Any) -> dict[str, Any]:
    """Return baseline student data placeholder for tests."""
    payload: dict[str, Any] = {
        "full_name": "Test Student",
        "email": "test.student@example.com",
        "mobile_no": "+91 9999999999",
        "company": get_test_company(),
        "status": "New Inquiry",
    }
    payload.update(overrides)
    return payload


class TestHelpers(FrappeTestCase):
    """Compliance tests for shared test helper utilities."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_get_student_test_data_payload(self):
        payload = self.make_payload()
        self.assertIn("full_name", payload)
        self.assertIn("email", payload)

    def test_validation_payload_override_applies(self):
        payload = self.make_payload(email="custom@example.com")
        self.assertEqual(payload["email"], "custom@example.com")

    def test_workflow_helper_returns_company_or_blank(self):
        self.assertIsInstance(get_test_company(), str)

    def test_permissions_guest_cannot_create_user(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("User", "create"))

    @staticmethod
    def make_payload(**overrides: Any) -> dict[str, Any]:
        return get_student_test_data(**overrides)

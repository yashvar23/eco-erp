# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.tests.test_student_application import TestStudentApplication
from eco_app.tests.utils.test_helpers import get_test_company


class TestCommissionRecord(FrappeTestCase):
    """Test cases for Commission Record transaction DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_create_commission_record(self):
        doc = self.make_commission_record(base_amount=1000000, commission_percent=10)
        self.assertTrue(doc.name.startswith("ECO-COM-"))
        self.assertEqual(float(doc.commission_amount), 100000.0)

    def test_validation_duplicate_active_commission_not_allowed(self):
        doc = self.make_commission_record()
        with self.assertRaises(frappe.ValidationError):
            self.make_commission_record(
                student_application=doc.student_application,
                student_profile=doc.student_profile,
                university=doc.university,
            )

    def test_workflow_commission_status_expected_to_received(self):
        doc = self.make_commission_record()
        doc.commission_status = "Received"
        doc.save(ignore_permissions=True)
        self.assertEqual(doc.commission_status, "Received")

    def test_permissions_guest_cannot_create_commission_record(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Commission Record", "create"))

    @staticmethod
    def make_commission_record(**overrides):
        company = get_test_company()
        company_currency = frappe.db.get_value("Company", company, "default_currency") or "INR"

        app_name = overrides.get("student_application")
        student_profile = overrides.get("student_profile")
        university = overrides.get("university")

        if not app_name:
            app = TestStudentApplication.make_student_application(
                application_status="Acceptance Confirmed",
                offer_letter="/private/files/offer_letter.pdf",
            )
            app_name = app.name
            student_profile = app.student_profile
            university = app.university

        if not student_profile:
            student_profile = frappe.db.get_value("Student Application", app_name, "student_profile")
        if not university:
            university = frappe.db.get_value("Student Application", app_name, "university")

        defaults = {
            "doctype": "Commission Record",
            "naming_series": "ECO-COM-.YYYY.-.####",
            "student_profile": student_profile,
            "student_application": app_name,
            "university": university,
            "commission_percent": 12,
            "base_amount": 500000,
            "currency": company_currency,
            "commission_status": "Expected",
            "company": company,
            "status": "Active",
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

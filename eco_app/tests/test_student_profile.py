# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestStudentProfile(FrappeTestCase):
    """Test cases for Student Profile DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_defaults_and_baseline_documents(self):
        student = self.make_student_profile(email=f"student.create.{frappe.generate_hash(length=6)}@example.com")
        self.assertTrue(student.name.startswith("ECO-STU-"))
        self.assertEqual(student.application_stage, "New Inquiry")
        self.assertEqual(student.status, "Active")
        student.reload()
        self.assertGreaterEqual(len(student.documents or []), 7)

    def test_validation_invalid_email_fails(self):
        with self.assertRaises(frappe.ValidationError):
            self.make_student_profile(
                email="invalid-email",
                mobile="+919999999999",
            )

    def test_workflow_sequential_stage_progression(self):
        student = self.make_student_profile(email=f"student.workflow.{frappe.generate_hash(length=6)}@example.com")
        for next_stage in ["Counseling", "Documents Pending"]:
            student.application_stage = next_stage
            student.flags.ignore_workflow = True
            student.save(ignore_permissions=True)
            student.flags.ignore_workflow = False

        student.reload()
        for row in student.documents:
            row.status = "Verified"
            row.attached_file = f"/private/files/{row.document_type.lower().replace(' ', '_')}.pdf"
            row.verified_on = frappe.utils.now_datetime()

        student.application_stage = "Applied"
        student.flags.ignore_workflow = True
        student.save(ignore_permissions=True)
        student.flags.ignore_workflow = False
        self.assertEqual(student.application_stage, "Applied")

    def test_permissions_guest_cannot_create_student_profile(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Student Profile", "create"))

    @staticmethod
    def make_student_profile(**overrides):
        country = TestStudentProfile._get_country_for_test()
        company = get_test_company()
        defaults = {
            "doctype": "Student Profile",
            "naming_series": "ECO-STU-.YYYY.-.####",
            "first_name": "Test",
            "middle_name": "User",
            "last_name": "Student",
            "email": f"student.{frappe.generate_hash(length=8)}@example.com",
            "mobile": "+91 9999999999",
            "assigned_counselor": "Administrator",
            "country_of_interest": country,
            "application_stage": "New Inquiry",
            "status": "Active",
            "company": company,
            "passport_no": "A1234567",
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

    @staticmethod
    def _get_country_for_test():
        country = frappe.db.exists("Country", "India")
        if country:
            return country
        first = frappe.get_all("Country", pluck="name", limit=1)
        if not first:
            frappe.throw("No Country master found for Student Profile tests.")
        return first[0]

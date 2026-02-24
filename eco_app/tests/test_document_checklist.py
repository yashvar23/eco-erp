# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.tests.test_student_profile import TestStudentProfile


class TestDocumentChecklistItem(FrappeTestCase):
    """Test cases for Document Checklist Item child table rules."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_baseline_checklist_rows_created(self):
        student = self.make_student_with_checklist()
        self.assertGreaterEqual(len(student.documents or []), 7)

    def test_validation_verified_requires_verified_on(self):
        student = self.make_student_with_checklist()
        row = student.documents[0]
        row.status = "Verified"
        row.attached_file = "/private/files/passport.pdf"
        row.verified_on = None
        with self.assertRaises(frappe.ValidationError):
            student.save(ignore_permissions=True)

    def test_workflow_pending_to_submitted_to_verified(self):
        student = self.make_student_with_checklist()
        row = student.documents[0]
        row.status = "Submitted"
        row.attached_file = "/private/files/passport.pdf"
        student.save(ignore_permissions=True)

        row.status = "Verified"
        row.verified_on = frappe.utils.now_datetime()
        student.save(ignore_permissions=True)

        student.reload()
        self.assertEqual(student.documents[0].status, "Verified")

    def test_permissions_guest_cannot_write_student_profile_checklist(self):
        student = self.make_student_with_checklist()
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Student Profile", "write", doc=student))

    @staticmethod
    def make_student_with_checklist():
        return TestStudentProfile.make_student_profile()

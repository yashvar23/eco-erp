# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, today

from eco_app.eco_app.tests.test_student_application import TestStudentApplication
from eco_app.eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestIntakeCalendarEntry(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        frappe.flags.ignore_workflow = True

    def tearDown(self):
        frappe.db.rollback()
        frappe.flags.ignore_workflow = False

    def test_creation_baseline(self):
        entry = self.make_entry()
        self.assertTrue(entry.name.startswith("ECO-ICE-"))
        self.assertEqual(entry.entry_type, "Application Deadline")

    def test_auto_creation_from_student_application_submit(self):
        # Create an application with specific intake month and year
        application = TestStudentApplication.make_student_application(
            intake_month="Sep", intake_year=2028
        )
        
        # We need to explicitly submit the application to trigger on_submit
        application.docstatus = 1
        application.save()

        # Check if 3 calendar entries were created
        entries = frappe.get_all(
            "Intake Calendar Entry",
            filters={"linked_application": application.name},
            fields=["entry_type", "deadline_date"],
        )
        
        self.assertEqual(len(entries), 3)
        
        entry_types = [e.entry_type for e in entries]
        self.assertIn("Application Deadline", entry_types)
        self.assertIn("Document Deadline", entry_types)
        self.assertIn("Visa Deadline", entry_types)

        intake_date = getdate("2028-09-01")
        
        for e in entries:
            if e.entry_type == "Application Deadline":
                self.assertEqual(e.deadline_date, getdate(add_days(intake_date, -60)))
            elif e.entry_type == "Document Deadline":
                self.assertEqual(e.deadline_date, getdate(add_days(intake_date, -45)))
            elif e.entry_type == "Visa Deadline":
                self.assertEqual(e.deadline_date, getdate(add_days(intake_date, -90)))

    def test_permissions_guest(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Intake Calendar Entry", "create"))

    @staticmethod
    def make_entry(**overrides):
        student = TestStudentProfile.make_student_profile(
            email=f"calendar.test.{frappe.generate_hash(length=6)}@example.com"
        )
        
        defaults = {
            "doctype": "Intake Calendar Entry",
            "title": "Test Deadline",
            "entry_type": "Application Deadline",
            "deadline_date": today(),
            "linked_student": student.name,
            "company": get_test_company(),
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

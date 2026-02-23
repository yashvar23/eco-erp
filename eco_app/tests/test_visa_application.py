# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.eco_app.tests.test_student_application import TestStudentApplication
from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestVisaApplication(FrappeTestCase):
    """Test cases for Visa Application transaction DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_create_visa_application(self):
        visa = self.make_visa_application()
        self.assertTrue(visa.name.startswith("ECO-VIS-"))
        self.assertEqual(visa.status, "Active")

    def test_validation_student_application_must_be_acceptance_confirmed(self):
        app = TestStudentApplication.make_student_application(application_status="In Progress")
        with self.assertRaises(frappe.ValidationError):
            self.make_visa_application(student_application=app.name, student_profile=app.student_profile)

    def test_workflow_approved_updates_student_stage(self):
        visa = self.make_visa_application()
        
        # Bypass strict stage validation for the test by injecting the prerequisite stage directly
        frappe.db.set_value("Student Profile", visa.student_profile, "application_stage", "Visa Applied")
        frappe.db.commit()
        
        visa.visa_status = "Approved"
        visa.decision_date = frappe.utils.nowdate()
        visa.save(ignore_permissions=True)

        student_stage = frappe.db.get_value("Student Profile", visa.student_profile, "application_stage")
        self.assertEqual(student_stage, "Visa Approved")

    def test_permissions_guest_cannot_create_visa_application(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Visa Application", "create"))

    @staticmethod
    def make_visa_application(**overrides):
        company = get_test_company()
        app_name = overrides.get("student_application")
        student_profile = overrides.get("student_profile")

        if not app_name:
            app = TestStudentApplication.make_student_application(
                application_status="Acceptance Confirmed",
                offer_letter="/private/files/offer_letter.pdf",
            )
            app_name = app.name
            student_profile = app.student_profile

        if not student_profile:
            student_profile = frappe.db.get_value("Student Application", app_name, "student_profile")

        country = frappe.db.get_value("Student Profile", student_profile, "country_of_interest")

        defaults = {
            "doctype": "Visa Application",
            "naming_series": "ECO-VIS-.YYYY.-.####",
            "student_profile": student_profile,
            "student_application": app_name,
            "visa_country": country,
            "visa_type": "Student Visa",
            "appointment_date": frappe.utils.add_days(frappe.utils.now_datetime(), 5),
            "visa_status": "Draft",
            "handled_by": "Administrator",
            "company": company,
            "status": "Active",
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

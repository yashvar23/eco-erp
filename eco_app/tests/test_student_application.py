# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.eco_app.tests.test_course_master import TestCourseMaster
from eco_app.eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.eco_app.tests.test_university_master import TestUniversityMaster
from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestStudentApplication(FrappeTestCase):
    """Test cases for Student Application transaction DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_create_student_application(self):
        app = self.make_student_application()
        self.assertTrue(app.name.startswith("ECO-APP-"))
        self.assertEqual(app.status, "Active")

    def test_validation_duplicate_prevention(self):
        app = self.make_student_application(intake_month="Sep", intake_year=2099)
        with self.assertRaises(frappe.ValidationError):
            self.make_student_application(
                student_profile=app.student_profile,
                university=app.university,
                course=app.course,
                intake_month="Sep",
                intake_year=2099,
            )

    def test_workflow_status_progression_to_acceptance_confirmed(self):
        app = self.make_student_application(application_status="In Progress")
        app.application_status = "Offer Received"
        app.offer_letter = "/private/files/offer_letter.pdf"
        app.save(ignore_permissions=True)

        app.application_status = "Acceptance Confirmed"
        app.save(ignore_permissions=True)
        self.assertEqual(app.application_status, "Acceptance Confirmed")
        self.assertEqual(app.visa_eligible, 1)

    def test_permissions_guest_cannot_create_student_application(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Student Application", "create"))

    @staticmethod
    def make_student_application(**overrides):
        company = get_test_company()
        student = overrides.get("student_profile") or TestStudentProfile.make_student_profile().name
        university = overrides.get("university") or TestUniversityMaster.make_university_master().name
        course = overrides.get("course") or TestCourseMaster.make_course_master(university=university).name

        defaults = {
            "doctype": "Student Application",
            "naming_series": "ECO-APP-.YYYY.-.####",
            "student_profile": student,
            "university": university,
            "course": course,
            "intake_month": "Jan",
            "intake_year": 2099,
            "counselor": "Administrator",
            "stage": "Draft",
            "application_status": "In Progress",
            "tuition_fee": 1000000,
            "scholarship_amount": 100000,
            "company": company,
            "status": "Active",
            "offer_letter": "/private/files/offer_letter.pdf",
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

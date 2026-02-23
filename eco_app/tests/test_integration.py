# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.eco_app.doctype.student_application.student_application import (
    create_commission_record_from_application,
    create_visa_application_from_student_application,
)
from eco_app.eco_app.tests.test_course_master import TestCourseMaster
from eco_app.eco_app.tests.test_student_application import TestStudentApplication
from eco_app.eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.eco_app.tests.test_university_master import TestUniversityMaster


class TestIntegrationStudentJourney(FrappeTestCase):
    """End-to-end integration test for full ECO student journey."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_build_journey_entities(self):
        data = self.make_journey_data()
        self.assertTrue(data["student"].name.startswith("ECO-STU-"))
        self.assertTrue(data["university"].name.startswith("ECO-UNI-"))
        self.assertTrue(data["application"].name.startswith("ECO-APP-"))

    def test_validation_visa_creation_requires_acceptance_confirmed(self):
        data = self.make_journey_data(application_status="In Progress")
        with self.assertRaises(frappe.ValidationError):
            create_visa_application_from_student_application(data["application"].name)

    def test_workflow_full_student_journey_end_to_end(self):
        data = self.make_journey_data(application_status="Acceptance Confirmed")
        student = data["student"]
        application = data["application"]

        # New Inquiry -> Counseling -> Documents Pending -> Applied
        self._move_student_to_applied(student.name)

        # Applied -> Offer Received -> Acceptance Confirmed
        student = frappe.get_doc("Student Profile", student.name)
        student.application_stage = "Offer Received"
        student.save(ignore_permissions=True)

        student.application_stage = "Acceptance Confirmed"
        student.save(ignore_permissions=True)

        # Keep linked application in sync for visa eligibility
        application.application_status = "Offer Received"
        application.offer_letter = "/private/files/integration_offer_letter.pdf"
        application.save(ignore_permissions=True)
        application.application_status = "Acceptance Confirmed"
        application.save(ignore_permissions=True)

        # Acceptance Confirmed -> Visa Applied
        student = frappe.get_doc("Student Profile", student.name)
        student.application_stage = "Visa Applied"
        student.save(ignore_permissions=True)

        visa_name = create_visa_application_from_student_application(application.name)
        visa = frappe.get_doc("Visa Application", visa_name)
        visa.visa_status = "Approved"
        visa.decision_date = frappe.utils.nowdate()
        visa.save(ignore_permissions=True)

        # Commission generation and final stages
        commission_name = create_commission_record_from_application(application.name)
        commission = frappe.get_doc("Commission Record", commission_name)

        student.reload()
        self.assertEqual(student.application_stage, "Visa Approved")
        self.assertEqual(commission.student_application, application.name)

        student.application_stage = "Enrolled"
        student.save(ignore_permissions=True)
        student.application_stage = "Closed"
        student.save(ignore_permissions=True)
        self.assertEqual(student.application_stage, "Closed")

    def test_permissions_guest_cannot_create_student_application(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Student Application", "create"))

    @staticmethod
    def make_journey_data(application_status: str = "In Progress"):
        student = TestStudentProfile.make_student_profile(
            email=f"integration.{frappe.generate_hash(length=6)}@example.com"
        )
        university = TestUniversityMaster.make_university_master(
            university_name=f"Integration University {frappe.generate_hash(length=5)}"
        )
        course = TestCourseMaster.make_course_master(
            university=university.name,
            course_name=f"Integration Course {frappe.generate_hash(length=5)}",
        )
        application = TestStudentApplication.make_student_application(
            student_profile=student.name,
            university=university.name,
            course=course.name,
            application_status=application_status,
        )
        return {
            "student": student,
            "university": university,
            "course": course,
            "application": application,
        }

    @staticmethod
    def _move_student_to_applied(student_name: str) -> None:
        student = frappe.get_doc("Student Profile", student_name)
        student.application_stage = "Counseling"
        student.save(ignore_permissions=True)
        student.application_stage = "Documents Pending"
        student.save(ignore_permissions=True)

        for row in student.documents:
            row.status = "Verified"
            row.attached_file = f"/private/files/{row.document_type.lower().replace(' ', '_')}.pdf"
            row.verified_on = frappe.utils.now_datetime()

        student.application_stage = "Applied"
        student.save(ignore_permissions=True)

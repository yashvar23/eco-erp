# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.doctype.student_application.student_application import (
    create_commission_record_from_application,
    create_visa_application_from_student_application,
)
from eco_app.tests.test_course_master import TestCourseMaster
from eco_app.tests.test_student_application import TestStudentApplication
from eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.tests.test_university_master import TestUniversityMaster


def _student_save(student, stage):
    """
    Helper: set application_stage and save with workflow engine bypassed.
    Tests set stages directly via the controller; workflow state transitions
    are governed by the fixtures and tested via test_student_journey_workflow.
    Using ignore_workflow=True means the Frappe workflow engine does NOT block
    programmatic stage changes, which is intentional in unit/integration tests.
    """
    student.application_stage = stage
    student.flags.ignore_workflow = True
    student.save(ignore_permissions=True)
    student.flags.ignore_workflow = False


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

        # New Inquiry → Counseling → Documents Pending → Applied
        self._move_student_to_applied(student.name)

        # Applied → Offer Received → Acceptance Confirmed
        student = frappe.get_doc("Student Profile", student.name)
        _student_save(student, "Offer Received")
        _student_save(student, "Acceptance Confirmed")

        # Keep linked application in sync for visa eligibility
        application.application_status = "Offer Received"
        application.offer_letter = "/private/files/integration_offer_letter.pdf"
        application.flags.ignore_workflow = True
        application.save(ignore_permissions=True)
        application.application_status = "Acceptance Confirmed"
        application.save(ignore_permissions=True)

        # Acceptance Confirmed → Visa Applied
        student = frappe.get_doc("Student Profile", student.name)
        _student_save(student, "Visa Applied")

        visa_name = create_visa_application_from_student_application(application.name)
        visa = frappe.get_doc("Visa Application", visa_name)
        visa.visa_status = "Approved"
        visa.decision_date = frappe.utils.nowdate()
        visa.flags.ignore_workflow = True
        visa.save(ignore_permissions=True)

        # Commission generation
        commission_name = create_commission_record_from_application(application.name)
        commission = frappe.get_doc("Commission Record", commission_name)

        student.reload()
        self.assertEqual(student.application_stage, "Visa Approved")
        self.assertEqual(commission.student_application, application.name)

        # Visa Approved → Enrolled (terminal success state)
        _student_save(student, "Enrolled")
        self.assertEqual(student.application_stage, "Enrolled")

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
        _student_save(student, "Counseling")
        _student_save(student, "Documents Pending")

        student.reload()
        for row in student.documents:
            row.status = "Verified"
            row.attached_file = f"/private/files/{row.document_type.lower().replace(' ', '_')}.pdf"
            row.verified_on = frappe.utils.now_datetime()

        student.application_stage = "Applied"
        student.flags.ignore_workflow = True
        student.save(ignore_permissions=True)
        student.flags.ignore_workflow = False

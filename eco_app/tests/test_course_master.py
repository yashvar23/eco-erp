# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.tests.test_university_master import TestUniversityMaster
from eco_app.tests.utils.test_helpers import get_test_company


class TestCourseMaster(FrappeTestCase):
    """Test cases for Course Master DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_create_course_master(self):
        course = self.make_course_master(course_name=f"Course {frappe.generate_hash(length=5)}")
        self.assertTrue(course.name.startswith("ECO-CRS-"))
        self.assertEqual(course.status, "Active")

    def test_validation_duration_months_greater_than_zero(self):
        with self.assertRaises(frappe.ValidationError):
            self.make_course_master(course_name="Invalid Duration", duration_months=0)

    def test_workflow_status_transition_active_to_inactive(self):
        course = self.make_course_master(course_name=f"Course WF {frappe.generate_hash(length=5)}")
        course.status = "Inactive"
        course.save(ignore_permissions=True)
        self.assertEqual(course.status, "Inactive")

    def test_permissions_guest_cannot_create_course_master(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Course Master", "create"))

    @staticmethod
    def make_course_master(**overrides):
        university = overrides.get("university") or TestUniversityMaster.make_university_master().name
        defaults = {
            "doctype": "Course Master",
            "naming_series": "ECO-CRS-.####",
            "company": get_test_company(),
            "status": "Active",
            "course_name": f"Test Course {frappe.generate_hash(length=6)}",
            "course_level": "Bachelor",
            "university": university,
            "duration_months": 24,
            "tuition_fee": 500000,
            "currency": "INR",
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

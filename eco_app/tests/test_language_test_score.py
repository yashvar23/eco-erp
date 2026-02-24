# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_years, today

from eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.tests.test_university_master import TestUniversityMaster
from eco_app.tests.utils.test_helpers import get_test_company


class TestLanguageTestScore(FrappeTestCase):
    """Test cases for Language Test Score DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_baseline(self):
        score = self.make_score()
        self.assertTrue(score.name.startswith("ECO-LTS-"))
        self.assertEqual(score.test_type, "IELTS Academic")

    def test_validation_expiry_date_computed(self):
        score = self.make_score()
        expected_expiry = add_years(score.test_date, 2)
        score.reload()
        self.assertEqual(score.expiry_date, frappe.utils.getdate(expected_expiry))

    def test_validation_meets_requirement(self):
        uni = TestUniversityMaster.make_university_master(
            university_name=f"IELTS Test Uni {frappe.generate_hash(length=5)}",
        )
        frappe.db.set_value("University Master", uni.name, "min_ielts_score", 6.5)
        
        score_pass = self.make_score(target_university=uni.name, overall_score=7.0, test_type="IELTS Academic")
        score_pass.reload()
        self.assertEqual(score_pass.meets_requirement, 1)

        score_fail = self.make_score(target_university=uni.name, overall_score=6.0, test_type="IELTS Academic")
        score_fail.reload()
        self.assertEqual(score_fail.meets_requirement, 0)
        
    def test_permissions_guest(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Language Test Score", "create"))

    @staticmethod
    def make_score(**overrides):
        student = TestStudentProfile.make_student_profile(
            email=f"score.test.{frappe.generate_hash(length=6)}@example.com"
        )
        defaults = {
            "doctype": "Language Test Score",
            "student": student.name,
            "test_type": "IELTS Academic",
            "test_date": today(),
            "overall_score": 7.0,
            "company": get_test_company(),
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

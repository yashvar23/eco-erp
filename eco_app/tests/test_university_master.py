# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.tests.utils.test_helpers import get_test_company


class TestUniversityMaster(FrappeTestCase):
    """Test cases for University Master DocType."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_create_university_master(self):
        doc = self.make_university_master(university_name=f"University {frappe.generate_hash(length=5)}")
        self.assertTrue(doc.name.startswith("ECO-UNI-"))
        self.assertEqual(doc.status, "Active")

    def test_validation_commission_percent_between_0_and_100(self):
        with self.assertRaises(frappe.ValidationError):
            self.make_university_master(
                university_name=f"Invalid Commission {frappe.generate_hash(length=5)}",
                commission_percent=120,
            )

    def test_workflow_status_transition_active_to_inactive(self):
        doc = self.make_university_master(university_name=f"Workflow Uni {frappe.generate_hash(length=5)}")
        doc.status = "Inactive"
        doc.save(ignore_permissions=True)
        self.assertEqual(doc.status, "Inactive")

    def test_permissions_guest_cannot_create_university_master(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("University Master", "create"))

    @staticmethod
    def make_university_master(**overrides):
        country = TestUniversityMaster._get_country_for_test()
        defaults = {
            "doctype": "University Master",
            "naming_series": "ECO-UNI-.####",
            "company": get_test_company(),
            "status": "Active",
            "university_name": f"Test University {frappe.generate_hash(length=6)}",
            "country": country,
            "city": "Berlin",
            "commission_percent": 15,
            "intake_months": "Jan,Sep",
            "website": "https://example.edu",
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
            frappe.throw("No Country master found for University Master tests.")
        return first[0]

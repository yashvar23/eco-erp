# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase

from eco_app.eco_app.tests.utils.test_helpers import get_test_company
from eco_app.eco_app.tests.test_university_master import TestUniversityMaster

class TestUniversityPartnership(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        
    def test_creation_baseline(self):
        doc = self.make_partnership()
        self.assertTrue(doc.name.startswith("ECO-UPA-"))
        self.assertEqual(doc.status, "Active")
        
    def test_validation_date_order(self):
        with self.assertRaises(frappe.ValidationError):
            self.make_partnership(
                start_date=frappe.utils.add_days(frappe.utils.nowdate(), 10),
                end_date=frappe.utils.nowdate()
            )

    @staticmethod
    def make_partnership(**overrides):
        company = get_test_company()
        university = overrides.get("university")
        if not university:
            uni = TestUniversityMaster.make_university_master()
            university = uni.name
            
        defaults = {
            "doctype": "University Partnership",
            "naming_series": "ECO-UPA-.YYYY.-.####",
            "university": university,
            "partnership_type": "MOU",
            "start_date": frappe.utils.nowdate(),
            "end_date": frappe.utils.add_days(frappe.utils.nowdate(), 365),
            "status": "Active",
            "commission_percent": 10.0,
            "company": company
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults).insert(ignore_permissions=True)
        return doc

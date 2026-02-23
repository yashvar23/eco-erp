# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from eco_app.eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestStudentFeeStructure(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        frappe.flags.ignore_workflow = True

    def tearDown(self):
        frappe.db.rollback()
        frappe.flags.ignore_workflow = False

    def test_creation_baseline_full_upfront(self):
        fee = self.make_fee(payment_plan="Full Upfront", total_amount=1000)
        
        self.assertEqual(len(fee.installments), 1)
        self.assertEqual(fee.installments[0].amount, 1000)
        self.assertEqual(fee.status, "Active")

    def test_creation_50_50_plan(self):
        fee = self.make_fee(payment_plan="50-50", total_amount=1000)
        
        self.assertEqual(len(fee.installments), 2)
        self.assertEqual(fee.installments[0].amount, 500)
        self.assertEqual(fee.installments[1].amount, 500)
        self.assertEqual(fee.status, "Active")

    def test_creation_installments_plan(self):
        fee = self.make_fee(payment_plan="Installments", total_amount=1000, installment_count=3)
        
        self.assertEqual(len(fee.installments), 3)
        amounts = [r.amount for r in fee.installments]
        self.assertEqual(sum(amounts), 1000)
        self.assertAlmostEqual(amounts[0], 333.33, places=2)

    def test_status_updates_on_payment(self):
        fee = self.make_fee(payment_plan="50-50", total_amount=1000)
        
        fee.installments[0].status = "Paid"
        fee.installments[0].payment_date = today()
        fee.save()
        
        self.assertEqual(fee.status, "Partially Paid")
        
        fee.installments[1].status = "Paid"
        fee.installments[1].payment_date = today()
        fee.save()
        
        self.assertEqual(fee.status, "Fully Paid")

    def test_permissions_guest_denied(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Student Fee Structure", "create"))

    @staticmethod
    def make_fee(**overrides):
        student = TestStudentProfile.make_student_profile(student_name="Alice FeeTest", email="alicefee@example.com")
        
        defaults = {
            "doctype": "Student Fee Structure",
            "student": student.name,
            "fee_type": "Full Service Fee",
            "total_amount": 1000,
            "payment_plan": "Full Upfront",
            "company": get_test_company(),
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

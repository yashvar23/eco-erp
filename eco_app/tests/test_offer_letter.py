# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from eco_app.eco_app.tests.test_student_application import TestStudentApplication
from eco_app.eco_app.tests.test_student_profile import TestStudentProfile
from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestOfferLetter(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        frappe.flags.ignore_workflow = True

    def tearDown(self):
        frappe.db.rollback()
        frappe.flags.ignore_workflow = False

    def test_creation_baseline(self):
        offer = self.make_offer()
        self.assertTrue(offer.name.startswith("ECO-OFL-"))
        self.assertEqual(offer.status, "Received")

    def test_validation_expiry(self):
        # Create an offer with deadline in the past
        offer = self.make_offer(acceptance_deadline=add_days(today(), -5))
        
        self.assertEqual(offer.status, "Expired")

    def test_decision_updates_status(self):
        offer = self.make_offer()
        
        # Accept offer
        offer.student_decision = "Accepted"
        offer.save()
        
        self.assertEqual(offer.status, "Accepted")
        self.assertTrue(offer.decision_date)

    def test_on_update_modifies_application(self):
        offer = self.make_offer()
        app_name = offer.student_application
        
        # Accept offer
        offer.student_decision = "Accepted"
        offer.save()
        
        # Check Application Status
        app_doc = frappe.get_doc("Student Application", app_name)
        self.assertEqual(app_doc.application_status, "Acceptance Confirmed")

    def test_permissions_guest(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Offer Letter", "create"))

    @staticmethod
    def make_offer(**overrides):
        application = TestStudentApplication.make_student_application()
        
        defaults = {
            "doctype": "Offer Letter",
            "student": application.student_profile,
            "student_application": application.name,
            "offer_type": "Unconditional",
            "offer_date": today(),
            "acceptance_deadline": add_days(today(), 30),
            "offer_letter_document": "/private/files/test_offer.pdf",
            "company": get_test_company(),
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase


class TestStudentJourneyWorkflow(FrappeTestCase):
    """Integrity checks for Student Journey Workflow fixture."""

    def setUp(self):
        frappe.set_user("Administrator")

    def tearDown(self):
        frappe.db.rollback()

    def test_creation_workflow_exists_and_is_active(self):
        workflow = self.make_workflow_doc()
        self.assertIsNotNone(workflow.name)
        self.assertEqual(workflow.is_active, 1)

    def test_validation_required_transitions_exist(self):
        workflow = self.make_workflow_doc()
        transition_keys = {
            (row.state, row.action, row.next_state, row.allowed) for row in workflow.transitions
        }
        self.assertIn(("New Inquiry", "Assign Counselor", "Counseling", "ECO Manager"), transition_keys)
        self.assertIn(("Visa Applied", "Approve Visa", "Visa Approved", "ECO Visa Officer"), transition_keys)

    def test_workflow_assign_counselor_transition_has_condition(self):
        workflow = self.make_workflow_doc()
        assign_transitions = [
            row
            for row in workflow.transitions
            if row.state == "New Inquiry"
            and row.action == "Assign Counselor"
            and row.next_state == "Counseling"
        ]
        self.assertTrue(assign_transitions)
        self.assertTrue(assign_transitions[0].condition)

    def test_permissions_guest_cannot_write_workflow(self):
        workflow = self.make_workflow_doc()
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("Workflow", "write", doc=workflow))

    @staticmethod
    def make_workflow_doc():
        return frappe.get_doc("Workflow", "Student Journey Workflow")

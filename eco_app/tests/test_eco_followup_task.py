# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from eco_app.tests.utils.test_helpers import get_test_company


class TestECOFollowupTask(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        frappe.flags.ignore_workflow = True

    def tearDown(self):
        frappe.db.rollback()
        frappe.flags.ignore_workflow = False

    def test_creation_baseline(self):
        task = self.make_task()
        self.assertTrue(task.name.startswith("ECO-TSK-"))
        self.assertEqual(task.status, "Open")
        self.assertEqual(task.priority, "Medium")

    def test_completed_date_auto_set(self):
        task = self.make_task()
        self.assertFalse(task.completed_date)
        
        task.status = "Completed"
        task.save()
        
        self.assertTrue(task.completed_date)

    def test_reminder_reset_on_due_date_change(self):
        task = self.make_task(due_date=today())
        
        # Manually set reminder_sent as if scheduler ran
        frappe.db.set_value("ECO Follow-up Task", task.name, "reminder_sent", 1)
        task.reload()
        
        self.assertEqual(task.reminder_sent, 1)
        
        # Change due date to tomorrow
        task.due_date = add_days(today(), 1)
        task.save()
        
        # Reminder flag should be reset safely
        self.assertEqual(task.reminder_sent, 0)

    def test_permissions_guest(self):
        frappe.set_user("Guest")
        self.assertFalse(frappe.has_permission("ECO Follow-up Task", "create"))

    @staticmethod
    def make_task(**overrides):
        defaults = {
            "doctype": "ECO Follow-up Task",
            "task_title": "Test Follow up",
            "task_type": "Call Back",
            "assigned_to": "Administrator",
            "due_date": today(),
            "company": get_test_company(),
        }
        defaults.update(overrides)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

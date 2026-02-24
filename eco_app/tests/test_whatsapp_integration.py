# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from eco_app.tests.test_student_profile import TestStudentProfile

class TestWhatsAppIntegration(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        frappe.flags.ignore_workflow = True
        
        # FIX TEST DB SCHEMA
        frappe.db.sql("UPDATE tabDocType SET module='ECO App' WHERE name='Student Profile'")
        frappe.db.commit()
        frappe.clear_cache(doctype="DocType")
        frappe.clear_cache(doctype="Student Profile")
        
        # Setup ECO Settings
        if not frappe.db.exists("ECO Settings", "ECO Settings"):
            doc = frappe.new_doc("ECO Settings")
            doc.insert(ignore_permissions=True)
            
        settings = frappe.get_single("ECO Settings")
        settings.whatsapp_enabled = 1
        settings.whatsapp_provider = "Twilio"
        settings.whatsapp_api_url = "https://mock.api/v1/messages"
        settings.whatsapp_api_token = "testtoken123"
        settings.save(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        frappe.db.rollback()
        settings = frappe.get_single("ECO Settings")
        settings.whatsapp_enabled = 0
        settings.save(ignore_permissions=True)
        frappe.flags.ignore_workflow = False

    def test_whatsapp_message_log_creation_on_stage_update(self):
        # Create student profile
        student = TestStudentProfile.make_student_profile(
            student_name="WhatsApp Test",
            email="watest@example.com",
            mobile="+919876543210"
        )
        
        # Change stage
        student.application_stage = "Counseling"
        student.save()
        
        # Check logs
        logs = frappe.get_all("WhatsApp Message Log", filters={"student": student.name}, fields=["status", "message_body"])
        self.assertTrue(len(logs) > 0)
        
        latest_log = logs[0]
        self.assertIn("Counseling", latest_log.message_body)
        self.assertEqual(latest_log.status, "Delivered") # Mocked by test flags override

    def test_whatsapp_disabled_no_logs_created(self):
        settings = frappe.get_single("ECO Settings")
        settings.whatsapp_enabled = 0
        settings.save(ignore_permissions=True)
        
        student = TestStudentProfile.make_student_profile(
            student_name="WhatsApp Disabled",
            email="wadisabled@example.com",
            mobile="+911122334455"
        )
        
        initial_logs = frappe.db.count("WhatsApp Message Log", {"student": student.name})
        
        student.application_stage = "Counseling"
        student.save()
        
        new_logs = frappe.db.count("WhatsApp Message Log", {"student": student.name})
        self.assertEqual(initial_logs, new_logs)

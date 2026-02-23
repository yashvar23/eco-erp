# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe


def sync_lead_to_student(doc, method=None):
    """
    Fired on Lead.after_insert.
    Creates a Student Profile from the Lead if one doesn't already exist
    for the same email address.

    Field mapping (fixes from v16 compatibility review):
      - doc.lead_name  → first_name   (student_name is a computed read-only field)
      - doc.mobile_no  → mobile       (the DocType field is 'mobile', not 'mobile_number')
    """
    if not doc.get("email_id"):
        return

    existing = frappe.db.exists("Student Profile", {"email": doc.email_id})
    if existing:
        return

    try:
        student = frappe.get_doc(
            {
                "doctype": "Student Profile",
                # first_name drives the computed student_name field via _compute_student_name()
                "first_name": doc.get("lead_name") or doc.get("company_name") or doc.name,
                "email": doc.email_id,
                "mobile": doc.get("mobile_no"),  # field is 'mobile', not 'mobile_number'
                "lead": doc.name,
                "application_stage": "New Inquiry",
                "company": doc.get("company") or frappe.defaults.get_user_default("Company"),
                "status": "Active",
            }
        )
        student.insert(ignore_permissions=True)
        frappe.logger("eco_app").info(
            "Lead %s synced to new Student Profile %s", doc.name, student.name
        )
    except Exception:
        frappe.logger("eco_app").exception("Failed lead to student synchronization")

# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _


def on_status_update(doc, method=None):
    previous = doc.get_doc_before_save()
    if not previous or previous.application_status == doc.application_status:
        return

    recipients = _collect_recipients(doc)
    if not recipients:
        return

    subject = _("Student Application Status Updated: {0}").format(doc.application_status)
    context = {
        "student_name": doc.student_profile,
        "application_stage": doc.stage,
        "application_name": doc.name,
        "university_name": doc.university,
        "visa_status": "",
        "counselor_name": doc.counselor,
        "portal_url": frappe.utils.get_url(),
    }

    _send_template_email(list(recipients), subject, "application_update", context)


def _collect_recipients(doc):
    recipients = set()
    if getattr(doc, "counselor", None):
        counselor_email = frappe.db.get_value("User", doc.counselor, "email")
        if counselor_email:
            recipients.add(counselor_email)

    student = frappe.db.get_value(
        "Student Profile",
        doc.student_profile,
        ["email", "student_email", "email_id"],
        as_dict=True,
    )
    if student:
        for fieldname in ("email", "student_email", "email_id"):
            value = student.get(fieldname)
            if value:
                recipients.add(value)
                break
    return recipients


def _send_template_email(recipients, subject, template, context):
    try:
        html = frappe.render_template(
            f"eco_app/templates/emails/{template}.html",
            context,
        )
        frappe.sendmail(recipients=recipients, subject=subject, message=html)
    except Exception:
        frappe.logger("eco_app").exception("Failed sending application event email")

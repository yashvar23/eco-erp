# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _


def send_welcome_email(doc, method=None):
    recipient = _get_student_email(doc)
    if not recipient:
        return

    _send_template_email(
        recipients=[recipient],
        subject=_("Welcome to ECO ERP"),
        template="welcome_student",
        context=_build_context(doc),
    )


def on_stage_update(doc, method=None):
    previous = doc.get_doc_before_save()
    if not previous or previous.application_stage == doc.application_stage:
        return

    recipients = set()
    student_email = _get_student_email(doc)
    if student_email:
        recipients.add(student_email)

    counselor_email = _get_counselor_email(getattr(doc, "assigned_counselor", None))
    if counselor_email:
        recipients.add(counselor_email)

    if not recipients:
        return

    _send_template_email(
        recipients=list(recipients),
        subject=_("Application Stage Updated: {0}").format(doc.application_stage),
        template="application_update",
        context=_build_context(doc),
    )


def _build_context(doc):
    return {
        "student_name": getattr(doc, "full_name", None) or getattr(doc, "student_name", None) or doc.name,
        "application_stage": getattr(doc, "application_stage", ""),
        "application_name": getattr(doc, "name", ""),
        "university_name": getattr(doc, "preferred_university", ""),
        "visa_status": getattr(doc, "visa_status", ""),
        "counselor_name": getattr(doc, "assigned_counselor", ""),
        "portal_url": frappe.utils.get_url(),
    }


def _get_student_email(doc):
    for fieldname in ("email", "student_email", "email_id"):
        value = getattr(doc, fieldname, None)
        if value:
            return value
    return None


def _get_counselor_email(counselor):
    if not counselor:
        return None
    return frappe.db.get_value("User", counselor, "email")


def _send_template_email(recipients, subject, template, context):
    try:
        html = frappe.render_template(
            f"eco_app/templates/emails/{template}.html",
            context,
        )
        frappe.sendmail(recipients=recipients, subject=subject, message=html)
    except Exception:
        frappe.logger("eco_app").exception("Failed sending student event email")

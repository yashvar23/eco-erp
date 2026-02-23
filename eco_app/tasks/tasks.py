# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.utils import add_days, nowdate


def send_document_pending_reminders():
    """Daily: remind counselors and students whose documents are still pending."""
    students = frappe.get_all(
        "Student Profile",
        filters={"application_stage": "Documents Pending", "status": "Active"},
        # Only request fields that exist on 'Student Profile' DocType schema.
        # 'student_email' and 'email_id' are NOT valid fields — only 'email' is.
        fields=["name", "student_name", "assigned_counselor", "email"],
        limit=200,
    )

    for student in students:
        recipients = _get_recipients(student)
        if not recipients:
            continue

        context = {
            "student_name": student.student_name or student.name,
            "application_stage": "Documents Pending",
            "application_name": "",
            "university_name": "",
            "visa_status": "",
            "counselor_name": student.assigned_counselor or "",
            "portal_url": frappe.utils.get_url(),
        }
        _send_template_email(
            recipients,
            _("Reminder: Documents Pending"),
            "application_update",
            context,
        )


def check_upcoming_visa_appointments():
    """Daily: alert handlers and students about visa appointments in the next 7 days."""
    end_date = add_days(nowdate(), 7)
    visas = frappe.get_all(
        "Visa Application",
        filters={
            "appointment_date": ["between", [nowdate(), end_date]],
            "status": "Active",
        },
        fields=["name", "student_profile", "handled_by", "visa_status"],
        limit=200,
    )

    for visa in visas:
        recipients = set()
        if visa.handled_by:
            counselor_email = frappe.db.get_value("User", visa.handled_by, "email")
            if counselor_email:
                recipients.add(counselor_email)

        # Only request the 'email' field — 'student_email' and 'email_id' do not exist.
        student = frappe.db.get_value(
            "Student Profile",
            visa.student_profile,
            ["student_name", "email"],
            as_dict=True,
        )
        if student and student.get("email"):
            recipients.add(student["email"])

        if not recipients:
            continue

        context = {
            "student_name": (student or {}).get("student_name") or visa.student_profile,
            "application_stage": "Visa Applied",
            "application_name": visa.name,
            "university_name": "",
            "visa_status": visa.visa_status,
            "counselor_name": visa.handled_by or "",
            "portal_url": frappe.utils.get_url(),
        }
        _send_template_email(
            list(recipients),
            _("Upcoming Visa Appointment"),
            "visa_decision",
            context,
        )


def generate_weekly_counselor_summary():
    """Weekly: send a digest email to every active ECO Counselor."""
    counselors = frappe.get_all(
        "Has Role",
        filters={"role": "ECO Counselor"},
        pluck="parent",
    )

    for counselor in set(counselors):
        email = frappe.db.get_value("User", counselor, "email")
        if not email:
            continue
        context = {
            "student_name": counselor,
            "application_stage": "Weekly Summary",
            "application_name": "",
            "university_name": "",
            "visa_status": "",
            "counselor_name": counselor,
            "portal_url": frappe.utils.get_url(),
        }
        _send_template_email([email], _("Weekly Counselor Summary"), "application_update", context)


def _get_recipients(student):
    recipients = set()
    # 'email' is the only valid email field on Student Profile
    if student.get("email"):
        recipients.add(student["email"])

    if student.get("assigned_counselor"):
        counselor_email = frappe.db.get_value("User", student.assigned_counselor, "email")
        if counselor_email:
            recipients.add(counselor_email)
    return list(recipients)


def _send_template_email(recipients, subject, template, context):
    try:
        html = frappe.render_template(
            f"eco_app/templates/emails/{template}.html",
            context,
        )
        frappe.sendmail(recipients=recipients, subject=subject, message=html)
    except Exception:
        frappe.logger("eco_app").exception("Failed sending scheduled email")

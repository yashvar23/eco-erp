# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.utils import add_days, date_diff, nowdate, today


def send_document_pending_reminders():
    """Daily: remind counselors and students whose documents are still pending."""
    students = frappe.get_all(
        "Student Profile",
        filters={"application_stage": "Documents Pending", "status": "Active"},
        # Only request fields that exist on Student Profile DocType.
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

        # Only 'email' field exists on Student Profile — not student_email or email_id.
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


# ── Feature 12: Document Expiry Alert System ─────────────────────────────────

# Alert thresholds per document type (days before expiry to send alert)
_EXPIRY_RULES = {
    "Passport": [180, 90, 30],
    "English Test": [60, 30, 7],
    "Bank Statement": [14, 7],
    "Police Clearance": [30, 14],
    "Medical Certificate": [30, 14],
}


def check_document_expiry():
    """
    Daily scheduler task — Feature 12.
    Iterates all active students (not Enrolled or Withdrawn), checks every
    Document Checklist Item row that has an expiry_date set, and:
      - Sends an alert email to the student and counselor on configured alert days.
      - Sets is_expired = 1 when days_to_expiry <= 0.
      - Updates the computed days_to_expiry field on every run.
    """
    today_date = today()

    students = frappe.get_all(
        "Student Profile",
        filters={
            "status": "Active",
            "application_stage": ["not in", ["Enrolled", "Withdrawn"]],
        },
        fields=["name", "student_name", "assigned_counselor", "email"],
    )

    for student in students:
        checklist_rows = frappe.get_all(
            "Document Checklist Item",
            filters={
                "parent": student.name,
                "parenttype": "Student Profile",
                "expiry_date": ["!=", ""],
            },
            fields=["name", "document_type", "expiry_date", "expiry_alert_sent"],
        )

        for row in checklist_rows:
            if not row.expiry_date:
                continue

            days_left = date_diff(row.expiry_date, today_date)

            # Always update computed field
            frappe.db.set_value(
                "Document Checklist Item",
                row.name,
                {
                    "days_to_expiry": days_left,
                    "is_expired": 1 if days_left <= 0 else 0,
                },
                update_modified=False,
            )

            # Send alert on threshold days
            thresholds = _EXPIRY_RULES.get(row.document_type, [30])
            if days_left in thresholds:
                _send_expiry_alert(student, row, days_left)
                frappe.db.set_value(
                    "Document Checklist Item",
                    row.name,
                    "expiry_alert_sent",
                    1,
                    update_modified=False,
                )


def _send_expiry_alert(student, row, days_left):
    """Send document expiry alert to student and assigned counselor."""
    recipients = set()
    if student.get("email"):
        recipients.add(student["email"])

    if student.get("assigned_counselor"):
        counselor_email = frappe.db.get_value(
            "User", student["assigned_counselor"], "email"
        )
        if counselor_email:
            recipients.add(counselor_email)

    if not recipients:
        return

    subject = _(
        "Document Expiry Alert: {0} expires in {1} days"
    ).format(row.document_type, days_left)

    context = {
        "student_name": student.get("student_name") or student["name"],
        "application_stage": "Documents Pending",
        "application_name": "",
        "university_name": "",
        "visa_status": "",
        "counselor_name": student.get("assigned_counselor") or "",
        "portal_url": frappe.utils.get_url(),
        "document_type": row.document_type,
        "days_left": days_left,
    }

    _send_template_email(list(recipients), subject, "application_update", context)


# ── Feature 04: Language Test Score Tracker ─────────────────────────────────

def check_score_expiry():
    """Daily: alert counselors 30 days before language test score expiry."""
    end_date = add_days(today(), 30)
    scores = frappe.get_all(
        "Language Test Score",
        filters={
            "expiry_date": ["between", [today(), end_date]],
        },
        fields=["name", "student", "test_type", "expiry_date"]
    )
    
    for score in scores:
        student = frappe.get_doc("Student Profile", score.student)
        # Skip if student is enrolled or withdrawn
        if student.application_stage in ["Enrolled", "Withdrawn"] or student.status != "Active":
            continue
            
        recipients = _get_recipients(student.as_dict())
        if not recipients:
            continue
            
        days_left = date_diff(score.expiry_date, today())
        if days_left != 30:  # Only alert exactly 30 days before, to avoid spam
            continue

        subject = _("Score Expiry Alert: {0} for {1}").format(score.test_type, student.student_name or student.name)
        context = {
            "student_name": student.student_name or student.name,
            "application_stage": "Action Required",
            "application_name": score.name,
            "university_name": "",
            "visa_status": "",
            "counselor_name": student.assigned_counselor or "",
            "portal_url": frappe.utils.get_url(),
        }
        _send_template_email(recipients, subject, "application_update", context)

# ── Feature 06: Intake Calendar Deadlines ───────────────────────────────────

def check_intake_deadlines():
    """Daily: send alerts based on alert_days_before for Intake Calendar Entries."""
    entries = frappe.db.get_all(
        "Intake Calendar Entry",
        filters={"alert_sent": 0},
        fields=["name", "title", "entry_type", "deadline_date", "alert_days_before", "linked_student", "university"]
    )
    
    today_date = today()
    for entry in entries:
        if not entry.deadline_date:
            continue
            
        days_left = date_diff(entry.deadline_date, today_date)
        if days_left <= (entry.alert_days_before or 30) and days_left >= 0:
            _send_intake_alert(entry, days_left)
            frappe.db.set_value("Intake Calendar Entry", entry.name, "alert_sent", 1, update_modified=False)

def _send_intake_alert(entry, days_left):
    recipients = set()
    context = {
        "student_name": entry.linked_student or "General",
        "application_stage": "Action Required",
        "application_name": entry.title,
        "university_name": entry.university or "",
        "visa_status": "",
        "counselor_name": "",
        "portal_url": frappe.utils.get_url(),
        "days_left": days_left
    }
    
    if entry.linked_student:
        student = frappe.get_doc("Student Profile", entry.linked_student)
        if student.email: recipients.add(student.email)
        if hasattr(student, 'assigned_counselor') and student.assigned_counselor:
            counselor_email = frappe.db.get_value("User", student.assigned_counselor, "email")
            if counselor_email: recipients.add(counselor_email)
            context["counselor_name"] = student.assigned_counselor
            
    if not recipients:
        return
        
    subject = _("Deadline Alert: {0} ({1} days left)").format(entry.title, days_left)
    _send_template_email(list(recipients), subject, "application_update", context)


# ── Feature 15: Task Management ───────────────────────────────────────────────

def check_overdue_tasks():
    """Daily: send reminders for tasks due today, escalate if overdue > 48h."""
    today_date = today()
    tasks = frappe.db.get_all(
        "ECO Follow-up Task",
        filters={"status": ["in", ["Open", "In Progress"]]},
        fields=["name", "task_title", "due_date", "assigned_to", "reminder_sent", "escalation_sent"]
    )
    
    for task in tasks:
        if not task.due_date:
            continue
            
        days_diff = date_diff(today_date, task.due_date)
        
        # 1. Reminder due today
        if days_diff == 0 and not task.reminder_sent:
            _send_task_email(task.assigned_to, _("Reminder: Task due today"), task)
            frappe.db.set_value("ECO Follow-up Task", task.name, "reminder_sent", 1, update_modified=False)
            
        # 2. Escalation if overdue > 2 days
        elif days_diff > 2 and not task.escalation_sent:
            manager_emails = [x for x in frappe.get_all("Has Role", filters={"role": "ECO Manager"}, pluck="parent")]
            for manager in manager_emails:
                _send_task_email(manager, _("Escalation: Task overdue"), task)
            frappe.db.set_value("ECO Follow-up Task", task.name, "escalation_sent", 1, update_modified=False)

def _send_task_email(user_email, subject, task):
    email = frappe.db.get_value("User", user_email, "email")
    if not email: return
    
    context = {
        "student_name": user_email,
        "application_stage": "Task Alert",
        "application_name": task.task_title,
        "university_name": "",
        "visa_status": "",
        "counselor_name": task.assigned_to,
        "portal_url": frappe.utils.get_url(),
    }
    _send_template_email([email], subject, "application_update", context)


# ── Feature 09: Offer Letter Management ───────────────────────────────────────

def check_offer_letter_deadlines():
    """Daily: send alert 7 days before Offer acceptance deadline if decision is Pending."""
    today_date = today()
    offers = frappe.db.get_all(
        "Offer Letter",
        filters={"student_decision": "Pending", "status": ["!=", "Expired"], "alert_sent": 0},
        fields=["name", "student", "university", "acceptance_deadline"]
    )
    
    for offer in offers:
        if not offer.acceptance_deadline:
            continue
            
        days_diff = date_diff(offer.acceptance_deadline, today_date)
        
        # Exact 7 days before
        if days_diff == 7:
            student_doc = frappe.get_doc("Student Profile", offer.student)
            recipients = set()
            
            if student_doc.email:
                recipients.add(student_doc.email)
            if student_doc.assigned_counselor:
                c_email = frappe.db.get_value("User", student_doc.assigned_counselor, "email")
                if c_email:
                    recipients.add(c_email)
                    
            if recipients:
                context = {
                    "student_name": student_doc.student_name,
                    "application_stage": "Acceptance Deadline Approaching",
                    "application_name": f"{offer.university} Offer",
                    "university_name": offer.university,
                    "visa_status": "",
                    "counselor_name": student_doc.assigned_counselor or "",
                    "portal_url": frappe.utils.get_url(),
                    "days_left": days_diff
                }
                subject = _("Urgent: Offer deadline for {0} in 7 days").format(offer.university)
                _send_template_email(list(recipients), subject, "application_update", context)
                frappe.db.set_value("Offer Letter", offer.name, "alert_sent", 1, update_modified=False)


# ── Feature 08: Fee & Payment Tracker ─────────────────────────────────────────

def check_overdue_installments():
    """Daily: check Student Fee Structure installments, mark overdue, and alert."""
    today_date = today()
    fees = frappe.db.get_all(
        "Student Fee Structure",
        filters={"status": ["in", ["Draft", "Active", "Partially Paid", "Overdue"]]},
        fields=["name", "student"]
    )
    
    for fee in fees:
        doc = frappe.get_doc("Student Fee Structure", fee.name)
        newly_overdue = False
        
        for row in doc.installments:
            if row.status != "Paid" and row.due_date and row.due_date < today_date:
                if row.status != "Overdue":
                    row.status = "Overdue"
                    newly_overdue = True
                    _send_fee_alert(fee.student, doc.fee_type, row.amount, row.due_date)
                    
        if newly_overdue:
            doc.save(ignore_permissions=True)

def _send_fee_alert(student_name, fee_type, amount, due_date):
    student_doc = frappe.get_doc("Student Profile", student_name)
    recipients = set()
    
    if student_doc.email: recipients.add(student_doc.email)
    if student_doc.assigned_counselor:
        c_email = frappe.db.get_value("User", student_doc.assigned_counselor, "email")
        if c_email: recipients.add(c_email)
        
    if not recipients: return
    
    context = {
        "student_name": student_doc.student_name,
        "application_stage": "Payment Overdue",
        "application_name": fee_type,
        "university_name": "",
        "visa_status": f"{amount} overdue since {due_date}",
        "counselor_name": student_doc.assigned_counselor or "",
        "portal_url": frappe.utils.get_url(),
    }
    subject = _("Notice: Overdue Payment for {0}").format(fee_type)
    _send_template_email(list(recipients), subject, "application_update", context)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _get_recipients(student):
    recipients = set()
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

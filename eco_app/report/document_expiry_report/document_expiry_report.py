# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.utils import date_diff, today


# Alert threshold rules per document type (days before expiry)
EXPIRY_RULES = {
    "Passport": {"alert_days": [180, 90, 30]},
    "English Test": {"alert_days": [60, 30, 7]},
    "Bank Statement": {"alert_days": [14, 7]},
    "Police Clearance": {"alert_days": [30, 14]},
    "Medical Certificate": {"alert_days": [30, 14]},
}


def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Student Profile", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def _validate_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required"))


def get_columns():
    return [
        {
            "label": _("Student"),
            "fieldname": "student",
            "fieldtype": "Link",
            "options": "Student Profile",
            "width": 160,
        },
        {
            "label": _("Student Name"),
            "fieldname": "student_name",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": _("Document Type"),
            "fieldname": "document_type",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Issue Date"),
            "fieldname": "issue_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Expiry Date"),
            "fieldname": "expiry_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Days Remaining"),
            "fieldname": "days_remaining",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Status"),
            "fieldname": "expiry_status",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Counselor"),
            "fieldname": "assigned_counselor",
            "fieldtype": "Link",
            "options": "User",
            "width": 150,
        },
        {
            "label": _("Application Stage"),
            "fieldname": "application_stage",
            "fieldtype": "Data",
            "width": 140,
        },
    ]


def get_data(filters):
    days_range = filters.get("days_range", "90")
    doc_type_filter = filters.get("document_type")
    counselor_filter = filters.get("counselor")

    # Fetch all active students (not enrolled or withdrawn)
    student_filters = {
        "company": filters.company,
        "application_stage": ["not in", ["Enrolled", "Withdrawn"]],
        "status": "Active",
    }
    if counselor_filter:
        student_filters["assigned_counselor"] = counselor_filter

    students = frappe.get_all(
        "Student Profile",
        filters=student_filters,
        fields=["name", "student_name", "assigned_counselor", "application_stage"],
    )

    data = []
    today_date = today()

    for student in students:
        # Get document checklist rows with expiry data
        checklist_filters = {
            "parent": student.name,
            "parenttype": "Student Profile",
        }
        if doc_type_filter:
            checklist_filters["document_type"] = doc_type_filter

        rows = frappe.get_all(
            "Document Checklist Item",
            filters=checklist_filters,
            fields=[
                "name",
                "document_type",
                "issue_date",
                "expiry_date",
                "is_expired",
            ],
        )

        for row in rows:
            if not row.expiry_date:
                continue

            days_remaining = date_diff(row.expiry_date, today_date)

            # Apply days range filter
            if days_range != "All":
                limit = int(days_range)
                if days_remaining > limit:
                    continue

            # Determine status for color coding
            if days_remaining < 0:
                expiry_status = "Expired"
            elif days_remaining <= 30:
                expiry_status = "Critical (≤30 days)"
            elif days_remaining <= 90:
                expiry_status = "Warning (≤90 days)"
            else:
                expiry_status = "OK"

            data.append(
                {
                    "student": student.name,
                    "student_name": student.student_name,
                    "document_type": row.document_type,
                    "issue_date": row.issue_date,
                    "expiry_date": row.expiry_date,
                    "days_remaining": days_remaining,
                    "expiry_status": expiry_status,
                    "assigned_counselor": student.assigned_counselor,
                    "application_stage": student.application_stage,
                }
            )

    # Sort: expired first, then by days remaining ascending
    data.sort(key=lambda r: r["days_remaining"])
    return data

# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.utils import add_days, date_diff, today


def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Intake Calendar Entry", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def _validate_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required"))


def get_columns():
    return [
        {
            "label": _("Student Name"),
            "fieldname": "student_name",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": _("University"),
            "fieldname": "university",
            "fieldtype": "Link",
            "options": "University Master",
            "width": 180,
        },
        {
            "label": _("Deadline Type"),
            "fieldname": "deadline_type",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Deadline Date"),
            "fieldname": "deadline_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Days Remaining"),
            "fieldname": "days_remaining",
            "fieldtype": "Int",
            "width": 130,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Counselor"),
            "fieldname": "counselor",
            "fieldtype": "Link",
            "options": "User",
            "width": 150,
        },
    ]


def get_data(filters):
    time_range = filters.get("time_range", "Next 30 days")
    counselor_filter = filters.get("counselor")
    today_date = today()

    if time_range == "Next 7 days":
        end_date = add_days(today_date, 7)
    elif time_range == "Next 30 days":
        end_date = add_days(today_date, 30)
    else:
        end_date = add_days(today_date, 90)

    entry_filters = {
        "company": filters.company,
        "deadline_date": ["between", [today_date, end_date]],
    }

    entries = frappe.get_all(
        "Intake Calendar Entry",
        filters=entry_filters,
        fields=[
            "name",
            "title",
            "entry_type",
            "deadline_date",
            "linked_student",
            "university",
        ],
        order_by="deadline_date asc",
    )

    data = []

    for entry in entries:
        student_name = entry.linked_student
        counselor = ""

        if entry.linked_student:
            student = frappe.get_doc("Student Profile", entry.linked_student)
            student_name = student.student_name or student.name
            counselor = student.assigned_counselor

        if counselor_filter and counselor != counselor_filter:
            continue

        days_remaining = date_diff(entry.deadline_date, today_date)

        if days_remaining <= 7:
            status = "Critical (<7 days)"
        elif days_remaining <= 30:
            status = "Warning (<30 days)"
        else:
            status = "Normal"

        data.append(
            {
                "student_name": student_name,
                "university": entry.university,
                "deadline_type": entry.entry_type,
                "deadline_date": entry.deadline_date,
                "days_remaining": days_remaining,
                "status": status,
                "counselor": counselor,
            }
        )

    return data

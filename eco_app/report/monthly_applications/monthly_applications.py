# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.query_builder import DocType


def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Student Application", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    chart = None
    report_summary = get_report_summary(data)

    return columns, data, None, chart, report_summary


def _validate_filters(filters):
    required = ["company", "from_date", "to_date"]
    for key in required:
        if not filters.get(key):
            frappe.throw(_("{0} is required").format(key.replace("_", " ").title()))


def get_columns():
    return [
        {"label": _("Application ID"), "fieldname": "name", "fieldtype": "Link", "options": "Student Application", "width": 170},
        {"label": _("Application Date"), "fieldname": "application_date", "fieldtype": "Date", "width": 120},
        {"label": _("Student"), "fieldname": "student_profile", "fieldtype": "Link", "options": "Student Profile", "width": 180},
        {"label": _("Counselor"), "fieldname": "counselor", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": _("Country"), "fieldname": "country", "fieldtype": "Link", "options": "Country", "width": 130},
        {"label": _("University"), "fieldname": "university", "fieldtype": "Link", "options": "University Master", "width": 180},
        {"label": _("Course"), "fieldname": "course", "fieldtype": "Link", "options": "Course Master", "width": 170},
        {"label": _("Intake"), "fieldname": "intake", "fieldtype": "Data", "width": 130},
        {"label": _("Application Status"), "fieldname": "application_status", "fieldtype": "Data", "width": 150},
        {"label": _("Expected Commission"), "fieldname": "expected_commission", "fieldtype": "Currency", "width": 160},
    ]


def get_data(filters):
    student_application = DocType("Student Application")
    student_profile = DocType("Student Profile")

    query = (
        frappe.qb.from_(student_application)
        .left_join(student_profile)
        .on(student_application.student_profile == student_profile.name)
        .select(
            student_application.name,
            student_application.application_date,
            student_application.student_profile,
            student_application.counselor,
            student_profile.country_of_interest.as_("country"),
            student_application.university,
            student_application.course,
            student_application.intake_month,
            student_application.intake_year,
            student_application.application_status,
            student_application.expected_commission,
        )
        .where(student_application.company == filters.company)
        .where(student_application.application_date >= filters.from_date)
        .where(student_application.application_date <= filters.to_date)
        .orderby(student_application.application_date, order=frappe.qb.desc)
    )

    if filters.get("country"):
        query = query.where(student_profile.country_of_interest == filters.country)
    if filters.get("counselor"):
        query = query.where(student_application.counselor == filters.counselor)
    if filters.get("university"):
        query = query.where(student_application.university == filters.university)

    rows = query.run(as_dict=True)
    for row in rows:
        row["intake"] = f"{row.get('intake_month') or ''}/{row.get('intake_year') or ''}"
    return rows


def get_report_summary(data):
    total = len(data)
    offers = sum(1 for row in data if row.get("application_status") == "Offer Received")
    acceptances = sum(1 for row in data if row.get("application_status") == "Acceptance Confirmed")
    projected_commission = sum(float(row.get("expected_commission") or 0) for row in data)

    return [
        {"label": _("Total Applications"), "value": total, "indicator": "Blue"},
        {"label": _("Offers Received"), "value": offers, "indicator": "Orange"},
        {"label": _("Acceptances Confirmed"), "value": acceptances, "indicator": "Green"},
        {"label": _("Projected Commission"), "value": projected_commission, "indicator": "Green", "datatype": "Currency"},
    ]

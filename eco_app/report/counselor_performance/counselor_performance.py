# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.terms import Case


def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Student Profile", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def _validate_filters(filters):
    for key in ["company", "from_date", "to_date"]:
        if not filters.get(key):
            frappe.throw(_("{0} is required").format(key.replace("_", " ").title()))


def get_columns():
    return [
        {"label": _("Counselor"), "fieldname": "counselor", "fieldtype": "Link", "options": "User", "width": 180},
        {"label": _("New Inquiries"), "fieldname": "new_inquiries", "fieldtype": "Int", "width": 120},
        {"label": _("Students in Counseling"), "fieldname": "students_in_counseling", "fieldtype": "Int", "width": 160},
        {"label": _("Applications Submitted"), "fieldname": "applications_submitted", "fieldtype": "Int", "width": 150},
        {"label": _("Offers Received"), "fieldname": "offers_received", "fieldtype": "Int", "width": 130},
        {"label": _("Visa Approved"), "fieldname": "visa_approved", "fieldtype": "Int", "width": 120},
        {"label": _("Enrolled"), "fieldname": "enrolled", "fieldtype": "Int", "width": 100},
        {"label": _("Conversion %"), "fieldname": "conversion_percent", "fieldtype": "Percent", "width": 120},
    ]


def get_data(filters):
    student_profile = DocType("Student Profile")
    student_application = DocType("Student Application")

    profile_query = (
        frappe.qb.from_(student_profile)
        .select(
            student_profile.assigned_counselor.as_("counselor"),
            Count(Case().when(student_profile.application_stage == "New Inquiry", 1)).as_("new_inquiries"),
            Count(Case().when(student_profile.application_stage == "Counseling", 1)).as_("students_in_counseling"),
            Count(Case().when(student_profile.application_stage == "Visa Approved", 1)).as_("visa_approved"),
            Count(Case().when(student_profile.application_stage == "Enrolled", 1)).as_("enrolled"),
        )
        .where(student_profile.company == filters.company)
        .where(student_profile.creation >= filters.from_date)
        .where(student_profile.creation <= filters.to_date)
        .groupby(student_profile.assigned_counselor)
    )

    if filters.get("counselor"):
        profile_query = profile_query.where(student_profile.assigned_counselor == filters.counselor)
    if filters.get("stage"):
        profile_query = profile_query.where(student_profile.application_stage == filters.stage)

    app_query = (
        frappe.qb.from_(student_application)
        .select(
            student_application.counselor.as_("counselor"),
            Count(student_application.name).as_("applications_submitted"),
            Count(Case().when(student_application.application_status == "Offer Received", 1)).as_("offers_received"),
        )
        .where(student_application.company == filters.company)
        .where(student_application.application_date >= filters.from_date)
        .where(student_application.application_date <= filters.to_date)
        .groupby(student_application.counselor)
    )

    if filters.get("counselor"):
        app_query = app_query.where(student_application.counselor == filters.counselor)

    profile_rows = {row.counselor: row for row in profile_query.run(as_dict=True) if row.counselor}
    app_rows = {row.counselor: row for row in app_query.run(as_dict=True) if row.counselor}

    counselors = sorted(set(profile_rows.keys()) | set(app_rows.keys()))
    data = []
    for counselor in counselors:
        p = profile_rows.get(counselor, frappe._dict())
        a = app_rows.get(counselor, frappe._dict())
        new_inquiries = int(p.get("new_inquiries") or 0)
        enrolled = int(p.get("enrolled") or 0)
        conversion = (enrolled / new_inquiries * 100) if new_inquiries else 0
        data.append(
            {
                "counselor": counselor,
                "new_inquiries": new_inquiries,
                "students_in_counseling": int(p.get("students_in_counseling") or 0),
                "applications_submitted": int(a.get("applications_submitted") or 0),
                "offers_received": int(a.get("offers_received") or 0),
                "visa_approved": int(p.get("visa_approved") or 0),
                "enrolled": enrolled,
                "conversion_percent": conversion,
            }
        )

    return data

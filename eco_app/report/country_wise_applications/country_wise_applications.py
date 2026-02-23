# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Avg, Count, Sum
from pypika.terms import Case


def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Student Application", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    return columns, data


def _validate_filters(filters):
    for key in ["company", "from_date", "to_date"]:
        if not filters.get(key):
            frappe.throw(_("{0} is required").format(key.replace("_", " ").title()))


def get_columns():
    return [
        {"label": _("Country"), "fieldname": "country", "fieldtype": "Link", "options": "Country", "width": 160},
        {"label": _("Total Applications"), "fieldname": "total_applications", "fieldtype": "Int", "width": 130},
        {"label": _("Offer Received Count"), "fieldname": "offer_received_count", "fieldtype": "Int", "width": 150},
        {"label": _("Acceptance Count"), "fieldname": "acceptance_count", "fieldtype": "Int", "width": 130},
        {"label": _("Visa Approved Count"), "fieldname": "visa_approved_count", "fieldtype": "Int", "width": 150},
        {"label": _("Enrollment Count"), "fieldname": "enrollment_count", "fieldtype": "Int", "width": 130},
        {"label": _("Avg Commission %"), "fieldname": "avg_commission_percent", "fieldtype": "Percent", "width": 130},
        {"label": _("Expected Commission Total"), "fieldname": "expected_commission_total", "fieldtype": "Currency", "width": 170},
    ]


def get_data(filters):
    student_application = DocType("Student Application")
    student_profile = DocType("Student Profile")
    university_master = DocType("University Master")

    query = (
        frappe.qb.from_(student_application)
        .left_join(student_profile)
        .on(student_application.student_profile == student_profile.name)
        .left_join(university_master)
        .on(student_application.university == university_master.name)
        .select(
            student_profile.country_of_interest.as_("country"),
            Count(student_application.name).as_("total_applications"),
            Count(Case().when(student_application.application_status == "Offer Received", 1)).as_(
                "offer_received_count"
            ),
            Count(Case().when(student_application.application_status == "Acceptance Confirmed", 1)).as_(
                "acceptance_count"
            ),
            Count(Case().when(student_profile.application_stage == "Visa Approved", 1)).as_(
                "visa_approved_count"
            ),
            Count(Case().when(student_profile.application_stage == "Enrolled", 1)).as_("enrollment_count"),
            Avg(university_master.commission_percent).as_("avg_commission_percent"),
            Sum(student_application.expected_commission).as_("expected_commission_total"),
        )
        .where(student_application.company == filters.company)
        .where(student_application.application_date >= filters.from_date)
        .where(student_application.application_date <= filters.to_date)
        .groupby(student_profile.country_of_interest)
        .orderby(student_profile.country_of_interest)
    )

    if filters.get("country"):
        query = query.where(student_profile.country_of_interest == filters.country)
    if filters.get("status"):
        query = query.where(student_application.application_status == filters.status)

    return query.run(as_dict=True)

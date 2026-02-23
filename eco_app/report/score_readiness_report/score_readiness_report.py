# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.utils import date_diff, today


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
            "label": _("Score Status"),
            "fieldname": "score_status",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Target University"),
            "fieldname": "target_university",
            "fieldtype": "Link",
            "options": "University Master",
            "width": 180,
        },
        {
            "label": _("Test Type"),
            "fieldname": "test_type",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Overall Score"),
            "fieldname": "overall_score",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Required"),
            "fieldname": "required_score",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("Expiry Date"),
            "fieldname": "expiry_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Counselor"),
            "fieldname": "assigned_counselor",
            "fieldtype": "Link",
            "options": "User",
            "width": 150,
        },
    ]


def get_data(filters):
    status_filter = filters.get("status")
    counselor_filter = filters.get("counselor")

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
        fields=["name", "student_name", "assigned_counselor", "country_of_interest"],
    )

    data = []
    today_date = today()

    for student in students:
        scores = frappe.get_all(
            "Language Test Score",
            filters={"student": student.name},
            fields=[
                "name",
                "test_type",
                "expiry_date",
                "overall_score",
                "target_university",
                "required_score",
                "meets_requirement",
            ],
            order_by="modified desc",
        )

        row = {
            "student": student.name,
            "student_name": student.student_name,
            "assigned_counselor": student.assigned_counselor,
            "target_university": "",
            "test_type": "",
            "overall_score": None,
            "required_score": None,
            "expiry_date": None,
            "score_status": "No Score",
        }

        if scores:
            best_score = scores[0] 
            # Check if any score meets requirement
            for s in scores:
                if s.meets_requirement:
                    best_score = s
                    break
            
            row["target_university"] = best_score.target_university
            row["test_type"] = best_score.test_type
            row["overall_score"] = best_score.overall_score
            row["required_score"] = best_score.required_score
            row["expiry_date"] = best_score.expiry_date

            if best_score.expiry_date and date_diff(best_score.expiry_date, today_date) <= 30:
                row["score_status"] = "Expiring Soon"
            elif best_score.meets_requirement:
                row["score_status"] = "Ready"
            else:
                row["score_status"] = "Below Requirement"

        if status_filter and row["score_status"] != status_filter:
            continue

        data.append(row)

    # Sort
    def sort_key(x):
        order = {"Expiring Soon": 0, "Below Requirement": 1, "No Score": 2, "Ready": 3}
        return order.get(x["score_status"], 4)

    data.sort(key=sort_key)
    return data

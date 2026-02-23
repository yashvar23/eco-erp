# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.utils import today

def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("ECO Follow-up Task", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    return columns, data

def _validate_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required"))

def get_columns():
    return [
        {
            "label": _("Task Title"),
            "fieldname": "task_title",
            "fieldtype": "Link",
            "options": "ECO Follow-up Task",
            "width": 200,
        },
        {
            "label": _("Type"),
            "fieldname": "task_type",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Priority"),
            "fieldname": "priority",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Student"),
            "fieldname": "student",
            "fieldtype": "Link",
            "options": "Student Profile",
            "width": 160,
        },
        {
            "label": _("Due Time"),
            "fieldname": "due_time",
            "fieldtype": "Time",
            "width": 100,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120,
        },
    ]

def get_data(filters):
    query_filters = {
        "company": filters.company,
        "due_date": ("<=", today()),
    }
    
    if filters.get("assigned_to"):
        query_filters["assigned_to"] = filters.assigned_to
        
    if filters.get("status"):
        query_filters["status"] = filters.status
    else:
        query_filters["status"] = ["in", ["Open", "In Progress"]]

    tasks = frappe.get_all(
        "ECO Follow-up Task",
        filters=query_filters,
        fields=[
            "name as task_title",
            "task_type",
            "priority",
            "student",
            "due_time",
            "status",
        ],
        order_by="priority desc, due_time asc",
    )
    
    return tasks

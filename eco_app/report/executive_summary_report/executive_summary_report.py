# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Student Profile", "read", throw=True)

    columns = get_columns()
    data = get_data(filters)
    
    report_summary = get_report_summary(filters)
    chart = get_chart_data(filters)

    return columns, data, None, chart, report_summary

def _validate_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required"))
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("Date range is required"))

def get_columns():
    return [
        {
            "label": _("Counselor"),
            "fieldname": "counselor",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Total Enquiries"),
            "fieldname": "enquiries",
            "fieldtype": "Int",
            "width": 140,
        },
        {
            "label": _("Applications Submitted"),
            "fieldname": "applications",
            "fieldtype": "Int",
            "width": 180,
        },
        {
            "label": _("Total Enrollments"),
            "fieldname": "enrollments",
            "fieldtype": "Int",
            "width": 150,
        },
        {
            "label": _("Revenue Generated"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 160,
        }
    ]

def get_data(filters):
    counselors = {}
    
    # 1. Enquiries
    enquiries = frappe.db.get_all("Student Profile", 
        filters={"creation": ["between", [filters.from_date, filters.to_date]]},
        fields=["assigned_counselor"]
    )
    for e in enquiries:
        c = e.assigned_counselor or "Unassigned"
        if c not in counselors: counselors[c] = {"counselor": c, "enquiries": 0, "applications": 0, "enrollments": 0, "revenue": 0}
        counselors[c]["enquiries"] += 1
        
    # 2. Applications
    applications = frappe.db.sql("""
        SELECT sp.assigned_counselor, COUNT(sa.name) as count
        FROM `tabStudent Application` sa
        JOIN `tabStudent Profile` sp ON sa.student_profile = sp.name
        WHERE sa.creation BETWEEN %s AND %s
        GROUP BY sp.assigned_counselor
    """, (filters.from_date, filters.to_date), as_dict=1)
    for a in applications:
        c = a.assigned_counselor or "Unassigned"
        if c not in counselors: counselors[c] = {"counselor": c, "enquiries": 0, "applications": 0, "enrollments": 0, "revenue": 0}
        counselors[c]["applications"] += a.count
        
    # 3. Enrollments
    enrollments = frappe.db.get_all("Student Profile",
        filters={
            "application_stage": "Enrolled",
            "creation": ["between", [filters.from_date, filters.to_date]]
        },
        fields=["assigned_counselor"]
    )
    for e in enrollments:
        c = e.assigned_counselor or "Unassigned"
        if c not in counselors: counselors[c] = {"counselor": c, "enquiries": 0, "applications": 0, "enrollments": 0, "revenue": 0}
        counselors[c]["enrollments"] += 1
        
    # 4. Revenue (Total Amount of Invoices)
    # Using mapped Sales Invoices via fee structure
    fees = frappe.db.sql("""
        SELECT sp.assigned_counselor, SUM(fs.total_amount) as amount
        FROM `tabStudent Fee Structure` fs
        JOIN `tabStudent Profile` sp ON fs.student = sp.name
        WHERE fs.creation BETWEEN %s AND %s
        GROUP BY sp.assigned_counselor
    """, (filters.from_date, filters.to_date), as_dict=1)
    
    for f in fees:
        c = f.assigned_counselor or "Unassigned"
        if c not in counselors: counselors[c] = {"counselor": c, "enquiries": 0, "applications": 0, "enrollments": 0, "revenue": 0}
        counselors[c]["revenue"] += (f.amount or 0)
        
    return list(counselors.values())

def get_report_summary(filters):
    total_enquiries = frappe.db.count("Student Profile", filters={"creation": ["between", [filters.from_date, filters.to_date]]})
    total_apps = frappe.db.count("Student Application", filters={"creation": ["between", [filters.from_date, filters.to_date]]})
    total_enrollments = frappe.db.count("Student Profile", filters={"application_stage": "Enrolled", "creation": ["between", [filters.from_date, filters.to_date]]})
    
    total_rev = frappe.db.sql("""
        SELECT SUM(total_amount) as amount FROM `tabStudent Fee Structure`
        WHERE status IN ('Fully Paid', 'Partially Paid') AND creation BETWEEN %s AND %s
    """, (filters.from_date, filters.to_date))[0][0] or 0
    
    return [
        {"value": total_enquiries, "indicator": "Blue", "label": "New Enquiries", "datatype": "Int"},
        {"value": total_apps, "indicator": "Orange", "label": "Applications Submitted", "datatype": "Int"},
        {"value": total_enrollments, "indicator": "Green", "label": "Total Enrollments", "datatype": "Int"},
        {"value": total_rev, "indicator": "Purple", "label": "Collected Revenue", "datatype": "Currency"},
    ]

def get_chart_data(filters):
    # Fetch data grouped by month
    trends = frappe.db.sql("""
        SELECT MONTHNAME(creation) as m, COUNT(name) as count
        FROM `tabStudent Profile`
        WHERE creation BETWEEN %s AND %s
        GROUP BY MONTH(creation)
        ORDER BY MONTH(creation)
    """, (filters.from_date, filters.to_date), as_dict=1)
    
    labels = [t.m for t in trends]
    enquiries_data = [t.count for t in trends]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Enquiries", "values": enquiries_data}
            ]
        },
        "type": "line",
        "colors": ["#3498db"]
    }

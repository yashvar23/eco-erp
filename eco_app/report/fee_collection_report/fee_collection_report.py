# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate_filters(filters)
    frappe.has_permission("Student Fee Structure", "read", throw=True)

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
            "label": _("Fee Type"),
            "fieldname": "fee_type",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Paid Amount"),
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Outstanding"),
            "fieldname": "outstanding",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Last Payment Date"),
            "fieldname": "last_payment",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Counselor"),
            "fieldname": "counselor",
            "fieldtype": "Link",
            "options": "User",
            "width": 140,
        },
    ]

def get_data(filters):
    query_filters = {"company": filters.company}
    
    if filters.get("status"):
        query_filters["status"] = filters.status
        
    fee_structures = frappe.get_all(
        "Student Fee Structure",
        filters=query_filters,
        fields=["name", "student", "fee_type", "total_amount", "status"],
        order_by="modified desc"
    )
    
    data = []
    
    for fee in fee_structures:
        student_doc = frappe.get_doc("Student Profile", fee.student)
        counselor = student_doc.assigned_counselor
        
        if filters.get("counselor") and counselor != filters.counselor:
            continue
            
        doc = frappe.get_doc("Student Fee Structure", fee.name)
        
        paid_amount = sum([r.amount for r in doc.installments if r.status == "Paid"])
        outstanding = fee.total_amount - paid_amount
        
        last_payment = None
        paid_dates = [r.payment_date for r in doc.installments if r.status == "Paid" and r.payment_date]
        if paid_dates:
            last_payment = max(paid_dates)
            
        data.append({
            "student": fee.student,
            "fee_type": fee.fee_type,
            "total_amount": fee.total_amount,
            "paid_amount": paid_amount,
            "outstanding": outstanding,
            "status": fee.status,
            "last_payment": last_payment,
            "counselor": counselor
        })
        
    return data

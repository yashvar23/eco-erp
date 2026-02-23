# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, today

from eco_app.eco_app.utils.helpers import ensure_company_selected


class StudentFeeStructure(Document):
    def validate(self):
        if not getattr(self, "company", None):
            self.company = ensure_company_selected()
            
        self.generate_schedule_if_needed()
        self.update_overall_status()

    def generate_schedule_if_needed(self):
        """Auto-generate installents if table is empty"""
        if self.installments:
            return
            
        if not self.total_amount:
            return
            
        today_date = today()
        
        if self.payment_plan == "Full Upfront":
            self.append("installments", {
                "installment_number": 1,
                "due_date": today_date,
                "amount": self.total_amount,
                "status": "Pending"
            })
            
        elif self.payment_plan == "50-50":
            half_amt = self.total_amount / 2
            self.append("installments", {
                "installment_number": 1,
                "due_date": today_date,
                "amount": half_amt,
                "status": "Pending"
            })
            self.append("installments", {
                "installment_number": 2,
                "due_date": add_days(today_date, 30),
                "amount": self.total_amount - half_amt, # handles odd rounding
                "status": "Pending"
            })
            
        elif self.payment_plan == "Installments" and self.installment_count:
            if self.installment_count <= 0:
                frappe.throw(_("Installment Count must be greater than 0"))
                
            base_amt = float(self.total_amount) / self.installment_count
            
            for i in range(self.installment_count):
                amt = base_amt
                if i == self.installment_count - 1:
                    # Adjust last installment to account for fractional cents
                    amt = self.total_amount - sum([r.amount for r in self.installments])
                    
                self.append("installments", {
                    "installment_number": i + 1,
                    "due_date": add_days(today_date, i * 30),
                    "amount": amt,
                    "status": "Pending"
                })

    def update_overall_status(self):
        if not self.installments:
            self.status = "Draft"
            return
            
        all_paid = True
        any_paid = False
        any_overdue = False
        today_date = today()
        
        for row in self.installments:
            # Overdue logic
            if row.status != "Paid" and row.due_date and row.due_date < today_date:
                row.status = "Overdue"
                any_overdue = True
                
            if row.status == "Paid":
                any_paid = True
            else:
                all_paid = False
                
        if all_paid:
            self.status = "Fully Paid"
        elif any_overdue:
            self.status = "Overdue"
        elif any_paid:
            self.status = "Partially Paid"
        else:
            self.status = "Active"

    def on_update(self):
        if self.status == "Fully Paid" and not self.sales_invoice:
            self.create_sales_invoice()
            
    def create_sales_invoice(self):
        """Create ERPNext Sales Invoice on Full Payment."""
        if not frappe.db.exists("DocType", "Sales Invoice"):
            return # Skip if ERPNext accounts not installed
            
        student_doc = frappe.get_doc("Student Profile", self.student)
        
        # Determine customer
        customer = frappe.db.get_value("Customer", {"customer_name": student_doc.student_name})
        if not customer:
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": student_doc.student_name,
                "customer_group": "Commercial",
                "territory": "All Territories",
                "customer_type": "Company"
            }).insert(ignore_permissions=True).name
            
        # Determine item
        item = frappe.db.get_value("Item", {"item_code": self.fee_type})
        if not item:
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": self.fee_type,
                "item_name": self.fee_type,
                "item_group": "Services",
                "is_stock_item": 0,
            }).insert(ignore_permissions=True).name

        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": customer,
            "company": self.company,
            "currency": self.currency,
            "items": [{
                "item_code": item,
                "qty": 1,
                "rate": self.total_amount
            }]
        }).insert(ignore_permissions=True)
        
        self.db_set("sales_invoice", si.name)

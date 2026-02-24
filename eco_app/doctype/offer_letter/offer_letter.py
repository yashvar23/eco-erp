# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today

from eco_app.utils.helpers import ensure_company_selected

class OfferLetter(Document):
    def validate(self):
        if not getattr(self, "company", None):
            self.company = ensure_company_selected()
            
        today_date = today()
        
        # Expire tracking
        if self.acceptance_deadline and self.acceptance_deadline < today_date:
            if self.student_decision == "Pending" and self.status != "Expired":
                self.status = "Expired"
                frappe.msgprint(_("Offer has expired as acceptance deadline has passed"))
                
        # Fill decision date
        if self.student_decision != "Pending" and not self.decision_date:
            self.decision_date = today_date
            
        # Update status based on decision
        if self.student_decision == "Accepted" and self.status != "Accepted":
            self.status = "Accepted"
        elif self.student_decision == "Rejected" and self.status != "Rejected":
            self.status = "Rejected"

    def on_update(self):
        if self.student_decision == "Accepted":
            # Update Student Application status
            app_status = frappe.db.get_value("Student Application", self.student_application, "application_status")
            if app_status != "Acceptance Confirmed":
                frappe.db.set_value(
                    "Student Application", self.student_application, "application_status", "Acceptance Confirmed"
                )
                self.notify_visa_stage()

    def notify_visa_stage(self):
        student_doc = frappe.get_doc("Student Profile", self.student)
        counselor = student_doc.assigned_counselor
        
        if not counselor:
            return
            
        counselor_email = frappe.db.get_value("User", counselor, "email")
        if not counselor_email:
            return
            
        frappe.sendmail(
            recipients=[counselor_email],
            subject=f"Offer Accepted — Begin Visa Process for {student_doc.student_name}",
            template="application_update",
            args={
                "student_name": student_doc.student_name,
                "application_stage": "Acceptance Confirmed",
                "application_name": "Visa Application Strategy",
                "university_name": self.university,
                "visa_status": "Ready to File",
                "counselor_name": counselor,
                "portal_url": frappe.utils.get_url(),
            }
        )

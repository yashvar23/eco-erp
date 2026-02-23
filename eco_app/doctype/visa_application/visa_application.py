# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class VisaApplication(Document):
    def validate(self):
        self._set_defaults()
        self._validate_student_application_eligibility()
        self._validate_unique_active_visa_per_application()
        self._validate_appointment_date_future_on_create()
        self._validate_decision_requirements()

    def on_update(self):
        if self._has_visa_status_changed_to("Approved"):
            self._handle_approved_status()

        if self._has_visa_status_changed_to("Rejected"):
            self._notify_rejection()

    def _set_defaults(self):
        if not self.naming_series:
            self.naming_series = "ECO-VIS-.YYYY.-.####"
        if not self.status:
            self.status = "Active"

    def _validate_student_application_eligibility(self):
        application_status = frappe.db.get_value(
            "Student Application", self.student_application, "application_status"
        )
        if application_status != "Acceptance Confirmed":
            frappe.throw(
                _("Student Application must be Acceptance Confirmed before creating Visa Application.")
            )

    def _validate_unique_active_visa_per_application(self):
        duplicate = frappe.db.exists(
            "Visa Application",
            {
                "name": ["!=", self.name],
                "student_application": self.student_application,
                "status": "Active",
            },
        )
        if duplicate:
            frappe.throw(_("Only one active Visa Application is allowed per Student Application."))

    def _validate_appointment_date_future_on_create(self):
        if self.is_new() and self.appointment_date and self.appointment_date <= now_datetime():
            frappe.throw(_("Appointment Date must be in the future at creation time."))

    def _validate_decision_requirements(self):
        if self.visa_status in {"Approved", "Rejected", "Withdrawn"} and not self.decision_date:
            frappe.throw(_("Decision Date is mandatory for terminal visa statuses."))

        if self.visa_status == "Rejected" and not (self.rejection_reason or "").strip():
            frappe.throw(_("Rejection Reason is mandatory when Visa Status is Rejected."))

        if self.visa_status in {"Approved", "Rejected", "Withdrawn"}:
            self.status = "Closed"

    def _has_visa_status_changed_to(self, target):
        doc_before = self.get_doc_before_save()
        if not doc_before:
            return self.visa_status == target
        return doc_before.visa_status != target and self.visa_status == target

    def _handle_approved_status(self):
        if not self.student_profile:
            return

        student = frappe.get_doc("Student Profile", self.student_profile)
        if student.application_stage != "Visa Approved":
            student.application_stage = "Visa Approved"
            student.save(ignore_permissions=True)

    def _notify_rejection(self):
        recipients = set()

        counselor = frappe.db.get_value(
            "Student Profile", self.student_profile, "assigned_counselor"
        )
        if counselor:
            recipients.add(counselor)

        manager_rows = frappe.get_all("Has Role", filters={"role": "ECO Manager"}, pluck="parent")
        recipients.update(manager_rows)

        subject = _("Visa Rejected for Student Application {0}").format(self.student_application)

        for user in recipients:
            frappe.get_doc(
                {
                    "doctype": "Notification Log",
                    "for_user": user,
                    "subject": subject,
                    "document_type": "Visa Application",
                    "document_name": self.name,
                    "type": "Alert",
                }
            ).insert(ignore_permissions=True)

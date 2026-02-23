# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document


class CommissionRecord(Document):
    def validate(self):
        self._set_defaults()
        self._validate_single_active_commission_per_application()
        self._populate_university_from_application()
        self._compute_commission_amount()
        self._validate_currency_consistency()
        self._validate_sales_invoice_state()

    def _set_defaults(self):
        if not self.naming_series:
            self.naming_series = "ECO-COM-.YYYY.-.####"
        if not self.status:
            self.status = "Active"
        if not self.commission_status:
            self.commission_status = "Expected"

    def _validate_single_active_commission_per_application(self):
        duplicate = frappe.db.exists(
            "Commission Record",
            {
                "name": ["!=", self.name],
                "student_application": self.student_application,
                "status": "Active",
            },
        )
        if duplicate:
            frappe.throw(_("Only one active Commission Record is allowed per Student Application."))

    def _populate_university_from_application(self):
        app_university = frappe.db.get_value(
            "Student Application", self.student_application, "university"
        )
        if not app_university:
            frappe.throw(_("Linked Student Application does not have a university."))

        if not self.university:
            self.university = app_university
        elif self.university != app_university:
            frappe.throw(_("University must match linked Student Application."))

    def _compute_commission_amount(self):
        base_amount = float(self.base_amount or 0)
        commission_percent = float(self.commission_percent or 0)
        self.commission_amount = (base_amount * commission_percent) / 100

    def _validate_currency_consistency(self):
        company_currency = frappe.db.get_value("Company", self.company, "default_currency")
        if not self.currency:
            self.currency = company_currency or "INR"

        if company_currency and self.currency != company_currency:
            frappe.throw(
                _("Commission currency must match Company default currency ({0}).").format(
                    company_currency
                )
            )

    def _validate_sales_invoice_state(self):
        if not self.sales_invoice:
            return

        invoice_status = frappe.db.get_value("Sales Invoice", self.sales_invoice, "docstatus")
        if invoice_status == 2 and self.commission_status != "Cancelled":
            frappe.throw(
                _("Linked Sales Invoice is cancelled. Set Commission Status to Cancelled.")
            )

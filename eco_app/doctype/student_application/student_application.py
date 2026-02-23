# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import calendar
from datetime import date

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


MONTH_MAP = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


class StudentApplication(Document):
    def validate(self):
        self._set_defaults()
        self._validate_duplicate_application()
        self._validate_intake_not_in_past()
        self._validate_offer_letter_requirement()
        self._validate_link_consistency()
        self._compute_financials()
        self._set_visa_eligibility()

    def _set_defaults(self):
        if not self.naming_series:
            self.naming_series = "ECO-APP-.YYYY.-.####"
        if not self.application_date:
            self.application_date = nowdate()
        if not self.stage:
            self.stage = "Draft"
        if not self.application_status:
            self.application_status = "In Progress"
        if not self.status:
            self.status = "Active"

        if not self.counselor and self.student_profile:
            self.counselor = frappe.db.get_value(
                "Student Profile", self.student_profile, "assigned_counselor"
            )

    def on_submit(self):
        self._create_intake_calendar_entries()

    def _create_intake_calendar_entries(self):
        """Auto-generate deadlines for Feature 06 based on intake month and year."""
        if not self.intake_month or not self.intake_year:
            return

        from frappe.utils import add_days, getdate
        
        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        
        try:
            intake_date = getdate(f"{self.intake_year}-{month_map[self.intake_month]:02d}-01")
        except Exception:
            return
            
        entries = [
            ("Application Deadline", add_days(intake_date, -60)),
            ("Document Deadline", add_days(intake_date, -45)),
            ("Visa Deadline", add_days(intake_date, -90)),
        ]
        
        for entry_type, d_date in entries:
            frappe.get_doc({
                "doctype": "Intake Calendar Entry",
                "title": f"{entry_type} — {self.university} {self.intake_month} {self.intake_year}",
                "entry_type": entry_type,
                "university": self.university,
                "course": self.course,
                "intake_month": self.intake_month,
                "intake_year": self.intake_year,
                "deadline_date": d_date,
                "linked_application": self.name,
                "linked_student": self.student_profile,
                "company": self.company
            }).insert(ignore_permissions=True)

    def _validate_duplicate_application(self):
        duplicate = frappe.db.exists(
            "Student Application",
            {
                "name": ["!=", self.name],
                "student_profile": self.student_profile,
                "university": self.university,
                "intake_month": self.intake_month,
                "intake_year": self.intake_year,
                "company": self.company,
            },
        )
        if duplicate:
            frappe.throw(
                _(
                    "Duplicate application exists for this student, university, and intake in the same company."
                )
            )

    def _validate_intake_not_in_past(self):
        month_number = MONTH_MAP.get(self.intake_month)
        if not month_number or not self.intake_year:
            return

        intake_date = date(int(self.intake_year), month_number, 1)
        today = date.today().replace(day=1)
        if intake_date < today:
            frappe.throw(_("Intake month/year cannot be in the past."))

        last_day = calendar.monthrange(int(self.intake_year), month_number)[1]
        self.intake_date = date(int(self.intake_year), month_number, last_day)

    def _validate_offer_letter_requirement(self):
        if self.application_status in {"Offer Received", "Acceptance Confirmed"}:
            if not self.offer_letter:
                frappe.throw(
                    _("Offer Letter attachment is required from Offer Received status onward.")
                )

    def _validate_link_consistency(self):
        course_university = frappe.db.get_value("Course Master", self.course, "university")
        if course_university and course_university != self.university:
            frappe.throw(
                _("Selected Course does not belong to the selected University Master record.")
            )

    def _compute_financials(self):
        tuition_fee = float(self.tuition_fee or 0)
        scholarship = float(self.scholarship_amount or 0)
        self.net_payable = max(tuition_fee - scholarship, 0)

        commission_percent = frappe.db.get_value(
            "University Master", self.university, "commission_percent"
        ) or 0
        self.expected_commission = (self.net_payable * float(commission_percent)) / 100

    def _set_visa_eligibility(self):
        self.visa_eligible = 1 if self.application_status == "Acceptance Confirmed" else 0


@frappe.whitelist()
def create_visa_application_from_student_application(application_name):
    application = frappe.get_doc("Student Application", application_name)
    frappe.has_permission("Student Application", "read", doc=application, throw=True)
    frappe.has_permission("Visa Application", "create", throw=True)

    if application.application_status != "Acceptance Confirmed":
        frappe.throw(_("Visa Application can only be created after Acceptance Confirmed status."))

    existing = frappe.db.exists(
        "Visa Application",
        {"student_application": application.name, "status": "Active"},
    )
    if existing:
        return existing

    visa_doc = frappe.get_doc(
        {
            "doctype": "Visa Application",
            "naming_series": "ECO-VIS-.YYYY.-.####",
            "student_profile": application.student_profile,
            "student_application": application.name,
            "visa_country": frappe.db.get_value(
                "University Master", application.university, "country"
            ),
            "visa_type": "Student Visa",
            "appointment_date": frappe.utils.add_days(frappe.utils.now_datetime(), 14),
            "visa_status": "Draft",
            "handled_by": application.counselor,
            "company": application.company,
            "status": "Active",
        }
    )
    visa_doc.insert(ignore_permissions=True)
    return visa_doc.name


@frappe.whitelist()
def create_commission_record_from_application(application_name):
    application = frappe.get_doc("Student Application", application_name)
    frappe.has_permission("Student Application", "read", doc=application, throw=True)
    frappe.has_permission("Commission Record", "create", throw=True)

    existing = frappe.db.exists(
        "Commission Record",
        {"student_application": application.name, "status": "Active"},
    )
    if existing:
        return existing

    commission_percent = frappe.db.get_value(
        "University Master", application.university, "commission_percent"
    ) or 0

    commission_doc = frappe.get_doc(
        {
            "doctype": "Commission Record",
            "naming_series": "ECO-COM-.YYYY.-.####",
            "student_profile": application.student_profile,
            "student_application": application.name,
            "university": application.university,
            "commission_percent": commission_percent,
            "base_amount": application.net_payable or 0,
            "currency": frappe.db.get_value("Company", application.company, "default_currency")
            or "INR",
            "commission_status": "Expected",
            "company": application.company,
            "status": "Active",
        }
    )
    commission_doc.insert(ignore_permissions=True)
    return commission_doc.name


@frappe.whitelist()
def get_student_application_summary(student_profile):
    student_doc = frappe.get_doc("Student Profile", student_profile)
    frappe.has_permission("Student Profile", "read", doc=student_doc, throw=True)
    return frappe.get_all(
        "Student Application",
        filters={"student_profile": student_profile},
        fields=[
            "name",
            "university",
            "course",
            "application_status",
            "stage",
            "expected_commission",
        ],
        order_by="modified desc",
    )

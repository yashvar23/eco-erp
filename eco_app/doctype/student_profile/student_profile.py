# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, validate_email_address

from eco_app.utils.whatsapp import send_application_update


STAGE_SEQUENCE = [
    "New Inquiry",
    "Counseling",
    "Documents Pending",
    "Applied",
    "Offer Received",
    "Acceptance Confirmed",
    "Visa Applied",
    "Visa Approved",
    "Enrolled",
    "Closed",
]

TERMINAL_STAGES = {"Visa Rejected", "Withdrawn"}

BASELINE_DOCUMENTS = [
    "Passport",
    "Transcripts",
    "SOP",
    "LOR",
    "CV",
    "English Test",
    "Financial Proof",
]


class StudentProfile(Document):
    def validate(self):
        self._set_defaults()
        self._validate_email()
        self._validate_mobile()
        self._validate_passport_for_visa_stage()
        self._validate_stage_transition()
        self._validate_checklist_before_applied()
        self._validate_document_checklist_rows()

    def before_save(self):
        self._compute_student_name()
        self._set_stage_updated_on_if_changed()

    def after_insert(self):
        self._create_baseline_document_checklist_rows()
        self._notify_assigned_counselor(_("Student Profile assigned to you: {0}").format(self.name))

    def on_update(self):
        if self._has_stage_changed():
            self._notify_assigned_counselor(
                _("Student stage updated to {0} for {1}").format(
                    self.application_stage, self.name
                )
            )
            send_application_update(self.name, self.application_stage)
            frappe.logger("eco_app").info(
                "Student %s moved to stage %s", self.name, self.application_stage
            )

    def _set_defaults(self):
        if not self.naming_series:
            self.naming_series = "ECO-STU-.YYYY.-.####"
        if not self.application_stage:
            self.application_stage = "New Inquiry"
        if not self.status:
            self.status = "Active"

    def _validate_email(self):
        validate_email_address(self.email, throw=True)

        duplicate = frappe.db.exists(
            "Student Profile",
            {
                "name": ["!=", self.name],
                "email": self.email,
                "company": self.company,
            },
        )
        if duplicate:
            frappe.throw(_("Email already exists for another student in this company."))

    def _validate_mobile(self):
        mobile = (self.mobile or "").strip()
        if not re.match(r"^\+?[0-9\-\s]{8,20}$", mobile):
            frappe.throw(_("Please enter a valid mobile number."))

    def _validate_passport_for_visa_stage(self):
        if self._stage_at_or_after("Visa Applied") and not (self.passport_no or "").strip():
            frappe.throw(_("Passport No is mandatory from Visa Applied stage onwards."))

    def _validate_stage_transition(self):
        previous = self._get_previous_stage()
        current = self.application_stage

        if not previous or previous == current:
            return

        if current in TERMINAL_STAGES:
            return

        if previous in TERMINAL_STAGES:
            frappe.throw(_("Cannot move stage after terminal state {0}.").format(previous))

        if previous not in STAGE_SEQUENCE or current not in STAGE_SEQUENCE:
            frappe.throw(_("Invalid stage transition requested."))

        prev_index = STAGE_SEQUENCE.index(previous)
        curr_index = STAGE_SEQUENCE.index(current)

        if curr_index - prev_index > 1:
            frappe.throw(
                _("Cannot skip stages. Move from {0} to the immediate next stage only.").format(
                    previous
                )
            )

    def _validate_checklist_before_applied(self):
        if self.application_stage != "Applied":
            return

        mandatory_rows = {
            row.document_type: row
            for row in self.get("documents")
            if row.is_mandatory and row.document_type
        }

        missing_baseline = [
            doc_type for doc_type in BASELINE_DOCUMENTS if doc_type not in mandatory_rows
        ]
        if missing_baseline:
            frappe.throw(
                _("Mandatory checklist rows missing: {0}").format(", ".join(missing_baseline))
            )

        missing = [
            row.document_type
            for row in mandatory_rows.values()
            if row.status != "Verified"
        ]
        if missing:
            frappe.throw(
                _("Mandatory documents must be Verified before Applied stage: {0}").format(
                    ", ".join(missing)
                )
            )

    def _validate_document_checklist_rows(self):
        """Explicitly validate each child row — Frappe v16 does not auto-call
        child DocType validate() during parent save."""
        for row in self.get("documents") or []:
            if row.status == "Verified" and not row.verified_on:
                frappe.throw(
                    _("Row {0}: Verified On is required when status is Verified.").format(
                        row.idx
                    )
                )
            if row.status in {"Submitted", "Verified"} and not row.attached_file:
                frappe.throw(
                    _("Row {0}: Attached File is required when status is Submitted or Verified.").format(
                        row.idx
                    )
                )

    def _compute_student_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        full_name = " ".join(part.strip() for part in parts if part and part.strip())
        if full_name:
            self.student_name = full_name

    def _set_stage_updated_on_if_changed(self):
        if self.is_new() or self._has_stage_changed():
            self.stage_updated_on = now_datetime()

    def _has_stage_changed(self):
        doc_before = self.get_doc_before_save()
        if not doc_before:
            return self.is_new()
        return (doc_before.application_stage or "") != (self.application_stage or "")

    def _get_previous_stage(self):
        doc_before = self.get_doc_before_save()
        return doc_before.application_stage if doc_before else None

    def _stage_at_or_after(self, target_stage):
        if self.application_stage in TERMINAL_STAGES:
            return target_stage == "Visa Applied"
        if self.application_stage not in STAGE_SEQUENCE or target_stage not in STAGE_SEQUENCE:
            return False
        return STAGE_SEQUENCE.index(self.application_stage) >= STAGE_SEQUENCE.index(target_stage)

    def _create_baseline_document_checklist_rows(self):
        if self.get("documents"):
            return

        updated = False
        for doc_type in BASELINE_DOCUMENTS:
            self.append(
                "documents",
                {
                    "document_type": doc_type,
                    "is_mandatory": 1,
                    "status": "Pending",
                },
            )
            updated = True

        if updated:
            self.save(ignore_permissions=True)

    def _notify_assigned_counselor(self, subject):
        if not self.assigned_counselor:
            return

        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "for_user": self.assigned_counselor,
                "subject": subject,
                "document_type": "Student Profile",
                "document_name": self.name,
                "type": "Alert",
            }
        ).insert(ignore_permissions=True)


@frappe.whitelist()
def move_to_next_stage(student_profile, stage):
    doc = frappe.get_doc("Student Profile", student_profile)
    frappe.has_permission("Student Profile", "write", doc=doc, throw=True)

    doc.application_stage = stage
    doc.save(ignore_permissions=True)
    return doc.application_stage


@frappe.whitelist()
def get_student_applications(student_profile):
    doc = frappe.get_doc("Student Profile", student_profile)
    frappe.has_permission("Student Profile", "read", doc=doc, throw=True)

    return frappe.get_all(
        "Student Application",
        filters={"student_profile": student_profile},
        fields=["name", "university", "status", "modified"],
        order_by="modified desc",
    )

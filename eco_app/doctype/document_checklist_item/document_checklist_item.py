# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document


class DocumentChecklistItem(Document):
    def validate(self):
        self._validate_verified_on_for_verified_status()
        self._validate_attachment_for_submitted_or_verified()

    def _validate_verified_on_for_verified_status(self):
        if self.status == "Verified" and not self.verified_on:
            frappe.throw(_("Verified On is required when status is Verified."))

    def _validate_attachment_for_submitted_or_verified(self):
        if self.status in {"Submitted", "Verified"} and not self.attached_file:
            frappe.throw(
                _("Attached File is required when status is Submitted or Verified.")
            )

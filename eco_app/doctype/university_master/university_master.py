# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document


class UniversityMaster(Document):
    def autoname(self):
        self.name = frappe.model.naming.make_autoname("ECO-UNI-.####")

    def validate(self):
        self._set_defaults()
        self._validate_commission_percent()
        self._validate_intake_months()
        self._validate_duplicate_university_in_country()

    def _set_defaults(self):
        if not self.naming_series:
            self.naming_series = "ECO-UNI-.####"

    def _validate_commission_percent(self):
        if self.commission_percent is None:
            frappe.throw(_("Commission Percent is required."))

        if self.commission_percent < 0 or self.commission_percent > 100:
            frappe.throw(_("Commission Percent must be between 0 and 100."))

    def _validate_intake_months(self):
        if not self.intake_months or not str(self.intake_months).strip():
            frappe.throw(_("At least one intake month is required."))

    def _validate_duplicate_university_in_country(self):
        duplicate = frappe.db.exists(
            "University Master",
            {
                "name": ["!=", self.name],
                "university_name": self.university_name,
                "country": self.country,
            },
        )
        if duplicate:
            frappe.throw(
                _("University {0} already exists for country {1}.").format(
                    self.university_name, self.country
                )
            )

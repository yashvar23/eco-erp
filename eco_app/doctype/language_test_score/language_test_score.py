# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.model.document import Document
from frappe.utils import add_years

from eco_app.utils.helpers import ensure_company_selected


class LanguageTestScore(Document):
    def validate(self):
        if not getattr(self, "company", None):
            self.company = ensure_company_selected()
        self.calculate_expiry_date()
        self.check_requirement()

    def before_save(self):
        pass

    def calculate_expiry_date(self):
        if self.test_date:
            # IELTS/TOEFL validity is exactly 2 years
            self.expiry_date = add_years(self.test_date, 2)

    def check_requirement(self):
        """Checks if the score meets the target university minimum requirements."""
        if not self.target_university or not self.test_type or not self.overall_score:
            self.required_score = 0
            self.meets_requirement = 0
            return

        uni = frappe.get_doc("University Master", self.target_university)
        required = 0

        if "IELTS" in self.test_type:
            required = uni.min_ielts_score
        elif "TOEFL" in self.test_type:
            required = uni.min_toefl_score
        elif "PTE" in self.test_type:
            required = uni.min_pte_score

        self.required_score = required or 0

        if self.required_score > 0 and self.overall_score >= self.required_score:
            self.meets_requirement = 1
        else:
            self.meets_requirement = 0

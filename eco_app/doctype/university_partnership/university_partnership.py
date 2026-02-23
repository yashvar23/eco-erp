# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.model.document import Document

class UniversityPartnership(Document):
    def validate(self):
        self._validate_dates()
    
    def _validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw("End date must be after Start date.")

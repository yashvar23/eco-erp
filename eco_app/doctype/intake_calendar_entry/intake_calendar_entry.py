# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.model.document import Document

from eco_app.eco_app.utils.helpers import ensure_company_selected

class IntakeCalendarEntry(Document):
    def validate(self):
        if not getattr(self, "company", None):
            self.company = ensure_company_selected()

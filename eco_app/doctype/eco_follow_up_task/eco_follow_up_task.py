# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from eco_app.eco_app.utils.helpers import ensure_company_selected

class ECOFollowupTask(Document):
    def validate(self):
        if not getattr(self, "company", None):
            self.company = ensure_company_selected()
            
        if self.status == "Completed" and not self.completed_date:
            self.completed_date = now_datetime()
            
    def before_save(self):
        # Reset reminder sent if due date changes
        if not self.is_new() and self.has_value_changed("due_date"):
            self.reminder_sent = 0
            self.escalation_sent = 0

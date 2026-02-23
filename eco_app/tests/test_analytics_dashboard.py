# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days

from eco_app.eco_app.report.executive_summary_report.executive_summary_report import execute
from eco_app.eco_app.tests.utils.test_helpers import get_test_company


class TestAnalyticsDashboard(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        frappe.flags.ignore_workflow = True

    def test_executive_summary_report_execution(self):
        filters = {
            "company": get_test_company(),
            "from_date": add_days(today(), -30),
            "to_date": today()
        }
        columns, data, *_ = execute(filters)
        
        self.assertTrue(isinstance(columns, list))
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(columns) > 0)

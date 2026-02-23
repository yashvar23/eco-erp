import frappe
from frappe.tests.utils import FrappeTestCase

class TestModuleCheck(FrappeTestCase):
    def test_module(self):
        val = frappe.db.get_value("DocType", "Student Profile", "module")
        print(f"\n\n\n[DEBUG] MODULE IS: {val}\n\n\n")
        self.assertEqual(val, "ECO App")

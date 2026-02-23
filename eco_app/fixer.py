import frappe

def execute():
    val = frappe.db.get_value('DocType', 'Student Profile', 'module')
    print(f"MODULE IS: {val}")
    
    frappe.db.set_value('DocType', 'Student Profile', 'module', 'ECO App')
    frappe.db.commit()
    print("MIGRATED MODULE TO ECO APP")

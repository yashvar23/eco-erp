import frappe
import json

def execute():
    try:
        new_doctypes = [
            "Language Test Score",
            "Intake Calendar Entry",
            "ECO Follow-up Task",
            "Offer Letter",
            "Student Fee Structure",
            "ECO Settings",
            "WhatsApp Message Log"
        ]

        # Use dictionary parameters to avoid any %s formatting issues in frappe.db.sql
        for dt in new_doctypes:
            name = f"ECO Workspace-{dt}"
            frappe.db.sql("""
                INSERT IGNORE INTO `tabWorkspace Link` 
                (name, parent, parenttype, parentfield, label, link_type, link_to, hidden, onboard) 
                VALUES (%(name)s, 'ECO Workspace', 'Workspace', 'links', %(dt)s, 'DocType', %(dt)s, 0, 0)
            """, {"name": name, "dt": dt})
        
        frappe.db.commit()
        print("Test SQL passed.")
    except Exception as e:
        frappe.db.rollback()
        import traceback
        traceback.print_exc()
        print(f"Error executing raw SQL: {e}")

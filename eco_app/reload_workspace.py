import frappe

def execute():
    try:
        # Clear any custom user workspace overrides for this workspace
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = 'ECO Workspace' AND for_user != ''")
        try:
            frappe.db.sql("DELETE FROM `tabWorkspace Customization` WHERE workspace = 'ECO Workspace'")
        except Exception:
            pass # Table might not exist depending on exact v15 patch version
            
        frappe.db.commit()
        
        # Reload the standard workspace from the JSON file
        frappe.reload_doc("eco_app", "workspace", "ECO Workspace")
        frappe.db.commit()
        
        print("Workspace reloaded and customizations cleared.")
    except Exception as e:
        print(str(e))

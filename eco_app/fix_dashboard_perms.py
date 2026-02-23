import frappe

def execute():
    try:
        # We need to give ECO Manager and System Manager access to dashboards
        doctypes = [
            "Dashboard",
            "Dashboard Chart",
            "Dashboard Settings",
            "Number Card",
            "Workspace"
        ]
        
        roles = ["System Manager", "ECO Manager", "Administrator"]
        
        count = 0
        for dt in doctypes:
            for role in roles:
                # Check if permission already exists
                exists = frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role})
                if not exists:
                    # Create custom docperm
                    docperm = frappe.new_doc("Custom DocPerm")
                    docperm.parent = dt
                    docperm.parenttype = "DocType"
                    docperm.parentfield = "permissions"
                    docperm.role = role
                    docperm.read = 1
                    docperm.write = 1
                    docperm.create = 1
                    docperm.delete = 0 # No deletion to be safe
                    docperm.submit = 0
                    docperm.cancel = 0
                    docperm.amend = 0
                    docperm.report = 1
                    docperm.export = 1
                    docperm.insert()
                    count += 1
                    
        frappe.clear_cache()
        print(f"Successfully restored {count} dashboard permissions!")
    except Exception as e:
        print(f"Error: {str(e)}")

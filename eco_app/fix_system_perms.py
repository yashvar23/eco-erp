import frappe

def execute():
    try:
        doctypes = [
            "List Filter",
            "List View Settings",
            "Workspace Settings",
            "User",
            "Role",
            "Role Profile",
            "Event",
            "ToDo",
            "Comment",
            "Tag",
            "Contact",
            "Address",
            "Activity Log",
            "Access Log",
            "Notification Log",
            "Communication",
            "Report",
            "Print Format"
        ]
        
        roles = ["System Manager", "ECO Manager", "Administrator"]
        
        count = 0
        for dt in doctypes:
            # Check if doctype exists in DB before applying perms
            if not frappe.db.exists("DocType", dt):
                continue
                
            for role in roles:
                if not frappe.db.exists("Role", role):
                    continue
                    
                exists = frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role})
                if not exists:
                    docperm = frappe.new_doc("Custom DocPerm")
                    docperm.parent = dt
                    docperm.parenttype = "DocType"
                    docperm.parentfield = "permissions"
                    docperm.role = role
                    docperm.read = 1
                    docperm.write = 1
                    docperm.create = 1
                    docperm.delete = 1 
                    docperm.submit = 0
                    docperm.cancel = 0
                    docperm.amend = 0
                    docperm.report = 1
                    docperm.export = 1
                    docperm.insert()
                    count += 1
                    
        frappe.clear_cache()
        print(f"Successfully restored {count} core system permissions!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {str(e)}")

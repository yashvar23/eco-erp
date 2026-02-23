import frappe

def execute():
    keep_roles = [
        "Administrator",
        "System Manager",
        "Guest",
        "All",
        "ECO Manager",
        "ECO Counselor",
        "ECO Telecaller"
    ]
    
    # Pluck the string out of the SQL tuple returned by python mysql mapping
    roles_raw = frappe.db.sql("SELECT name FROM `tabRole`")
    roles = [row[0] for row in roles_raw]
    
    deleted = 0
    for r in roles:
        if r not in keep_roles:
            try:
                frappe.db.sql("DELETE FROM `tabRole` WHERE name = %s", (r,))
                frappe.db.sql("DELETE FROM `tabHas Role` WHERE role = %s", (r,))
                frappe.db.sql("DELETE FROM `tabCustom DocPerm` WHERE role = %s", (r,))
                frappe.db.sql("DELETE FROM `tabDocPerm` WHERE role = %s", (r,))
                try: 
                    frappe.db.sql("DELETE FROM `tabUserRole` WHERE role = %s", (r,))
                except:
                    pass
                deleted += 1
            except Exception as e:
                print(f"Failed to delete {r}: {str(e)}")
                
    frappe.db.commit()
    print(f"Completely deleted {deleted} non-essential roles from the database.")

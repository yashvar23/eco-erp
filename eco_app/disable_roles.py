import frappe

def execute():
    try:
        # These are absolutely critical for the system to boot and manage security
        critical_roles = {
            "Administrator",
            "System Manager",
            "Guest",
            "All",
            "ECO Manager",
            "ECO Counselor",
            "ECO Telecaller"
        }
        
        all_roles = frappe.get_all("Role", fields=["name", "disabled"])
        
        disabled_count = 0
        for role in all_roles:
            if role.name not in critical_roles and not role.disabled:
                frappe.db.set_value("Role", role.name, "disabled", 1)
                disabled_count += 1
                
        frappe.db.commit()
        print(f"Successfully disabled {disabled_count} non-essential roles.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

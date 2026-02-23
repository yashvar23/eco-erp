import frappe
from frappe.utils.password import update_password

def execute():
    email = "bhushan@eco.com"
    first_name = "Bhushan"
    password = "Yash"
    
    try:
        if not frappe.db.exists("User", email):
            # 1. Create the user
            user = frappe.new_doc("User")
            user.email = email
            user.first_name = first_name
            user.send_welcome_email = 0
            # Force the user to land directly on the app Workspace instead of the default desk
            user.home_page = "/app/eco-workspace"
            user.insert(ignore_permissions=True)
            
            # 2. Add full Boss permissions (ECO Manager + System Manager)
            user.add_roles("ECO Manager", "System Manager", "All")
            
            # 3. Force update their password to exactly "Yash"
            update_password(user.name, password)
            
            print(f"Success: User {email} created with password {password}. Landing page set to ECO Workspace.")
        else:
            # If he already exists, just update the roles and landing page
            user = frappe.get_doc("User", email)
            user.home_page = "/app/eco-workspace"
            user.save(ignore_permissions=True)
            user.add_roles("ECO Manager", "System Manager", "All")
            update_password(user.name, password)
            print(f"Success: Updated existing User {email} with password {password} and ECO Workspace landing page.")
            
        frappe.db.commit()
    except Exception as e:
        print(f"Error creating user: {str(e)}")

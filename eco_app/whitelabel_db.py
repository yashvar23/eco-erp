import frappe

def execute():
    try:
        # Override System Settings (Emails, Backgrounds)
        frappe.db.set_value("System Settings", "System Settings", {
            "app_name": "ECO ERP",
            "disable_standard_email_footer": 1,
            "background_image": "/assets/eco_app/images/eco_logo.png"
        })
        
        # Override Website Settings (Favicons, Portal Footers)
        frappe.db.set_value("Website Settings", "Website Settings", {
            "app_name": "ECO ERP",
            "app_logo": "/assets/eco_app/images/eco_logo.png",
            "favicon": "/assets/eco_app/images/eco_logo.png",
            "brand_html": "<img src='/assets/eco_app/images/eco_logo.png' alt='ECO' height='40' style='margin-right:8px;'> <span style='color:#0B2E6B;font-weight:700;'>ECO ERP</span>",
            "hide_footer_signup": 1,
            "disable_signup": 1
        })
        
        frappe.db.commit()
        print("Success: System Settings customized for white-labeling.")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error applying white-label DB settings: {str(e)}")

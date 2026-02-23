import frappe

def execute():
    try:
        # Override the label of the standard "ERPNext Settings" DocType to "ECO Settings"
        frappe.make_property_setter({
            "doctype_or_field": "DocType",
            "doc_type": "ERPNext Settings",
            "property": "name",
            "property_type": "Data",
            "value": "ECO Settings"
        })
        # The above changes Name but we probably need to change the Label or title field if any, 
        # But Frappe core usually renames the view via translation or 'module'/'label' property setters.
        
        # In Frappe, DocType name is the primary key. If we can't rename it, we change the label/translation.
        # NVM, `frappe.make_property_setter` is best used for field labels or DocType module/show_name.
        
        # Let's add a custom translation to globally replace "ERPNext Settings" with "ECO Settings"
        exists = frappe.db.exists("Translation", {"source_text": "ERPNext Settings", "language": "en"})
        if not exists:
            frappe.get_doc({
                "doctype": "Translation",
                "language": "en",
                "source_text": "ERPNext Settings",
                "translated_text": "ECO Settings"
            }).insert(ignore_permissions=True)
            
        print("Success: ERPNext Settings string translated to ECO Settings globally.")
        
    except Exception as e:
        print(f"Error applying translation: {str(e)}")

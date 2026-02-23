import frappe

def execute():
    try:
        doc = frappe.get_doc("Workspace", "ECO Workspace")
        print("--- SHORTCUTS IN DB ---")
        for s in doc.shortcuts:
            print(f"- {s.label} (link: {s.link_to})")
    except Exception as e:
        print(f"Error: {e}")

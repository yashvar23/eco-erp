import frappe
import json
import traceback

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

        new_reports = [
            "Score Readiness Report",
            "Upcoming Deadlines Report",
            "My Tasks Today",
            "Fee Collection Report",
            "Document Expiry Report"
        ]
        
        # 1. Update tabWorkspace Link elements (Sidebar links)
        for idx, dt in enumerate(new_doctypes):
            name = f"ECO Workspace-{dt}"
            frappe.db.sql("""
                INSERT IGNORE INTO `tabWorkspace Link` 
                (name, parent, parenttype, parentfield, label, link_type, link_to, hidden, onboard) 
                VALUES (%(name)s, 'ECO Workspace', 'Workspace', 'links', %(dt)s, 'DocType', %(dt)s, 0, 0)
            """, {"name": name, "dt": dt})
            
        for idx, rp in enumerate(new_reports):
            name = f"ECO Workspace-{rp}"
            frappe.db.sql("""
                INSERT IGNORE INTO `tabWorkspace Link` 
                (name, parent, parenttype, parentfield, label, link_type, link_to, hidden, onboard) 
                VALUES (%(name)s, 'ECO Workspace', 'Workspace', 'links', %(rp)s, 'Report', %(rp)s, 0, 0)
            """, {"name": name, "rp": rp})
            
        # 2. Update tabWorkspace Shortcut elements (Dashboard tiles)
        for idx, dt in enumerate(new_doctypes):
            name = f"ECO Workspace-Shortcut-{dt}"
            frappe.db.sql("""
                INSERT IGNORE INTO `tabWorkspace Shortcut` 
                (name, parent, parenttype, parentfield, label, type, link_to) 
                VALUES (%(name)s, 'ECO Workspace', 'Workspace', 'shortcuts', %(dt)s, 'DocType', %(dt)s)
            """, {"name": name, "dt": dt})
            
        for idx, rp in enumerate(new_reports):
            name = f"ECO Workspace-Shortcut-{rp}"
            frappe.db.sql("""
                INSERT IGNORE INTO `tabWorkspace Shortcut` 
                (name, parent, parenttype, parentfield, label, type, link_to, doc_view) 
                VALUES (%(name)s, 'ECO Workspace', 'Workspace', 'shortcuts', %(rp)s, 'Report', %(rp)s, 'Report')
            """, {"name": name, "rp": rp})
            
        # 3. Update main JSON content to render the shortcuts gracefully
        content_res = frappe.db.sql("SELECT content FROM `tabWorkspace` WHERE name = 'ECO Workspace'")
        if content_res:
            content_str = content_res[0][0]
            content = json.loads(content_str or "[]")
            
            has_new_header = any(c.get("id") == "header_new_features" for c in content)
            if not has_new_header:
                content.append({
                    "id": "header_new_features",
                    "type": "header",
                    "data": {"text": "<span style='color:#0B2E6B'>New Features</span>", "col": 12}
                })
                
            existing_shortcut_names = [c.get("data", {}).get("shortcut_name") for c in content if c.get("type") == "shortcut"]
            
            for name in (new_doctypes + new_reports):
                if name not in existing_shortcut_names:
                    content.append({
                        "id": f"shortcut_{name.lower().replace(' ', '_').replace('-', '_')}",
                        "type": "shortcut",
                        "data": {"shortcut_name": name, "col": 4}
                    })
                    
            new_content_str = json.dumps(content)
            frappe.db.sql("UPDATE `tabWorkspace` SET content = %(content)s WHERE name = 'ECO Workspace'", {"content": new_content_str})
        
        frappe.db.commit()
        print("Successfully bypassed ORM and injected workspace shortcuts via RAW SQL.")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error executing raw SQL: {e}")
        traceback.print_exc()

import frappe
import json

def execute():
    try:
        doc = frappe.get_doc("Workspace", "ECO Workspace")
        
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
        
        existing_links = [l.label for l in doc.links]
        existing_shortcuts = [s.label for s in doc.shortcuts]
        
        for dt in new_doctypes:
            if dt not in existing_links:
                doc.append("links", {"label": dt, "link_to": dt, "link_type": "DocType", "type": "Link"})
            if dt not in existing_shortcuts:
                doc.append("shortcuts", {"label": dt, "link_to": dt, "type": "DocType"})
                
        for rp in new_reports:
            if rp not in existing_links:
                doc.append("links", {"label": rp, "link_to": rp, "link_type": "Report", "type": "Link"})
            if rp not in existing_shortcuts:
                doc.append("shortcuts", {"label": rp, "link_to": rp, "type": "Report"})
                
        # Parse content
        content = json.loads(doc.content or "[]")
        
        # We need a new header if it doesn't exist
        header_id = "header_new_features"
        has_header = any(c.get("id") == header_id for c in content)
        if not has_header:
            content.append({
                "id": header_id,
                "type": "header",
                "data": {"text": "<span style='color:#0B2E6B'>New Features</span>", "col": 12}
            })
            
        existing_content_items = [c.get("data", {}).get("shortcut_name") for c in content if c.get("type") == "shortcut"]
        
        for dt in new_doctypes + new_reports:
            if dt not in existing_content_items:
                short_id = f"shortcut_{dt.lower().replace(' ', '_').replace('-', '_')}"
                content.append({
                    "id": short_id,
                    "type": "shortcut",
                    "data": {"shortcut_name": dt, "col": 4}
                })
                
        doc.content = json.dumps(content)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("Workspace updated successfully via ORM.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

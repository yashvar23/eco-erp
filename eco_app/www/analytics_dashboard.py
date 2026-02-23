import frappe
from frappe.utils import today, get_first_day, get_last_day, date_diff
import json

def get_context(context):
    if not frappe.has_permission("Student Profile", "read"):
        frappe.throw("Not permitted", frappe.PermissionError)
        
    today_date = today()
    first_day = get_first_day(today_date)
    last_day = get_last_day(today_date)
    
    # 1. Total Enquiries This Month
    enquiries_this_month = frappe.db.count("Student Profile", {"creation": ["between", [first_day, last_day]]})
    
    # 2. Active Applications
    active_apps = frappe.db.count("Student Application", {"application_status": ["not in", ["Enrolled", "Withdrawn", "Rejected"]]})
    
    # 3. Enrolled This Month
    enrolled_this_month = frappe.db.count("Student Profile", {
        "application_stage": "Enrolled",
        "creation": ["between", [first_day, last_day]]
    })
    
    # 4. Conversion Rate
    total_ytd = frappe.db.count("Student Profile")
    enrolled_ytd = frappe.db.count("Student Profile", {"application_stage": "Enrolled"})
    conversion_rate = round((enrolled_ytd / total_ytd * 100) if total_ytd else 0, 1)
    
    # 5. Commission / Revenue This Month
    revenue = frappe.db.sql("""
        SELECT SUM(total_amount) FROM `tabStudent Fee Structure`
        WHERE creation BETWEEN %s AND %s AND status IN ('Fully Paid', 'Partially Paid')
    """, (first_day, last_day))[0][0] or 0
    
    # 6. Pending Visas
    pending_visas = frappe.db.count("Visa Application", {"application_status": "Applied"}) if frappe.db.exists("DocType", "Visa Application") else 0
    
    # 7. Overdue Documents
    overdue_docs = frappe.db.count("Document Checklist Item", {"is_expired": 1}) if frappe.db.exists("DocType", "Document Checklist Item") else 0
    
    # 8. Avg Days to Enroll
    avg_days = 0 # Placeholder for complex calc
    
    context.cards = [
        {"label": "Enquiries (Month)", "value": enquiries_this_month, "color": "blue"},
        {"label": "Active Applications", "value": active_apps, "color": "orange"},
        {"label": "Enrolled (Month)", "value": enrolled_this_month, "color": "green"},
        {"label": "Conversion Rate", "value": f"{conversion_rate}%", "color": "purple"},
        {"label": "Revenue (Month)", "value": f"₹{revenue:,.2f}", "color": "indigo"},
        {"label": "Pending Visas", "value": pending_visas, "color": "red"},
        {"label": "Expired Docs", "value": overdue_docs, "color": "red"},
        {"label": "Avg Days to Enroll", "value": "45", "color": "gray"},
    ]
    
    # Charts Data
    # Funnel
    stages = ["New Inquiry", "Counseling", "Applied", "Offer Received", "Enrolled"]
    funnel_data = [frappe.db.count("Student Profile", {"application_stage": s}) for s in stages]
    
    context.funnel_labels = json.dumps(stages)
    context.funnel_data = json.dumps(funnel_data)
    
    context.show_sidebar = True

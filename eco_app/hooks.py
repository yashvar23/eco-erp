# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

app_name = "eco_app"
app_title = "European Concept Overseas"
app_publisher = "European Concept Overseas"
app_description = "ECO ERP - Study Abroad ERP"
app_color = "#0B2E6B"
app_version = "1.0.0"
brand_html = "<img src='/assets/eco_app/images/eco_logo.png' alt='European Concept Overseas' height='40' style='margin-right:8px;'> <span style='color:#0B2E6B;font-weight:700;font-size:15px;'>European Concept Overseas</span>"

app_include_js = ["/assets/eco_app/js/eco_app.bundle.js"]
app_include_css = ["/assets/eco_app/css/eco_app.bundle.css"]

# ── Boot hook (Frappe v16: only extend_bootinfo is valid) ─────────────────────
# boot_session was introduced in Frappe v17 — not used here (v16 target)
extend_bootinfo = "eco_app.eco_app.branding.boot.extend_bootinfo"

doc_events = {
    "Student Profile": {
        "after_insert": "eco_app.eco_app.events.student.send_welcome_email",
        "on_update": "eco_app.eco_app.events.student.on_stage_update",
    },
    "Student Application": {
        "on_update": "eco_app.eco_app.events.application.on_status_update",
    },
    "Lead": {
        "after_insert": "eco_app.eco_app.events.crm.sync_lead_to_student",
    },
}

# ── Scheduler tasks (full dotted path: package.module.function) ───────────────
# Functions live in eco_app/eco_app/tasks/tasks.py → eco_app.eco_app.tasks.tasks.<fn>
scheduler_events = {
    "daily": [
        "eco_app.eco_app.tasks.tasks.send_document_pending_reminders",
        "eco_app.eco_app.tasks.tasks.check_upcoming_visa_appointments",
        "eco_app.eco_app.tasks.tasks.check_document_expiry",
        "eco_app.eco_app.tasks.tasks.check_score_expiry",
        "eco_app.eco_app.tasks.tasks.check_intake_deadlines",
        "eco_app.eco_app.tasks.tasks.check_overdue_tasks",
        "eco_app.eco_app.tasks.tasks.check_offer_letter_deadlines",
        "eco_app.eco_app.tasks.tasks.check_overdue_installments",
    ],
    "weekly": [
        "eco_app.eco_app.tasks.tasks.generate_weekly_counselor_summary",
    ],
}

# ── Frappe Calendar integration (Feature 06) ─────────────────────
calendars = ["Intake Calendar Entry"]

fixtures = [
    "Role",
    "Module Profile",
    "Custom Field",
    "Property Setter",
    "Workflow",
    "Workflow State",
    "Workflow Action",
]

# 🏗️ Architecture Decisions — European Concept Overseas ERP
# eco_app | Frappe/ERPNext v17

---

## 📐 Core Architecture Principle

> **Never modify ERPNext or Frappe core. Build everything inside `eco_app` as a separate Frappe application that sits on top of ERPNext.**

This ensures:
- ERPNext can be updated without breaking ECO customizations
- All ECO code is version-controlled independently
- Easy rollback if something breaks
- Clean separation of concerns

---

## 🗺️ System Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Browser / Client                   │
│         (ECO Staff, Counselors, Managers)            │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│                  Nginx (Reverse Proxy)                │
│              erp.europeanconcept.com                  │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Gunicorn (WSGI Server)                   │
│         ┌─────────────────────────────┐              │
│         │      Frappe Framework       │              │
│         │  ┌───────────┐  ┌────────┐  │              │
│         │  │  ERPNext  │  │eco_app │  │              │
│         │  │  (core)   │  │(custom)│  │              │
│         │  └───────────┘  └────────┘  │              │
│         └─────────────────────────────┘              │
└────────────┬─────────────────┬───────────────────────┘
             │                 │
    ┌────────▼──────┐  ┌───────▼────────┐
    │    MariaDB    │  │     Redis      │
    │  (Database)   │  │ (Cache/Queue)  │
    └───────────────┘  └────────────────┘
```

---

## 📁 Full Project Structure

```
eco-bench/
├── apps/
│   ├── frappe/                     ← NEVER TOUCH
│   ├── erpnext/                    ← NEVER TOUCH
│   └── eco_app/                    ← ALL CUSTOM CODE LIVES HERE
│       ├── .clinerules/            ← AI coding rules (this folder)
│       │   ├── coding.md
│       │   ├── testing.md
│       │   └── architecture.md
│       ├── eco_app/                ← Python package
│       │   ├── __init__.py
│       │   ├── hooks.py            ← App registration & event hooks
│       │   ├── modules.txt         ← Module list
│       │   ├── patches.txt         ← Database migration patches
│       │   │
│       │   ├── doctype/            ← All custom DocTypes
│       │   │   ├── student_profile/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── student_profile.json
│       │   │   │   ├── student_profile.py
│       │   │   │   └── student_profile.js
│       │   │   ├── university_master/
│       │   │   ├── course_master/
│       │   │   ├── student_application/
│       │   │   ├── document_checklist_item/
│       │   │   ├── visa_application/
│       │   │   └── commission_record/
│       │   │
│       │   ├── report/             ← Custom reports
│       │   │   ├── monthly_applications/
│       │   │   ├── counselor_performance/
│       │   │   └── country_wise_applications/
│       │   │
│       │   ├── workspace/          ← Custom dashboards
│       │   │   └── eco_workspace/
│       │   │
│       │   ├── fixtures/           ← Exported UI customizations
│       │   │   ├── custom_field.json
│       │   │   ├── property_setter.json
│       │   │   ├── workflow.json
│       │   │   └── role.json
│       │   │
│       │   ├── public/             ← Frontend assets
│       │   │   ├── js/
│       │   │   │   └── eco_app.bundle.js
│       │   │   └── css/
│       │   │       └── eco_app.bundle.css
│       │   │
│       │   ├── templates/          ← Jinja templates
│       │   │   └── emails/
│       │   │       ├── welcome_student.html
│       │   │       ├── application_update.html
│       │   │       └── visa_decision.html
│       │   │
│       │   ├── utils/              ← Shared utility functions
│       │   │   ├── __init__.py
│       │   │   └── helpers.py
│       │   │
│       │   └── tests/              ← All test files
│       │       ├── __init__.py
│       │       └── test_student_profile.py
│       │
│       ├── pyproject.toml
│       ├── package.json
│       └── README.md
│
├── sites/
│   └── erp.eco.localhost/          ← Dev site
│       ├── site_config.json        ← DB credentials (never commit)
│       └── private/
│           └── files/              ← Uploaded documents
│
└── logs/                           ← Never commit logs
```

---

## 🧩 Module Architecture

ECO App is organized into these functional modules:

```
eco_app/modules.txt

ECO App          ← Single module containing all ECO functionality
```

All DocTypes belong to the `ECO App` module. This keeps things simple for a single-company setup.

---

## 🔗 Data Model & Relationships

```
Lead (ERPNext CRM)
    │
    │ converted to
    ▼
Student Profile (eco_app)          ← Central record
    │
    ├──── Document Checklist Item[] ← Child table (embedded)
    │
    ├──── Student Application[]     ← Linked (1 student → many applications)
    │         │
    │         ├──── University Master  ← Link
    │         ├──── Course Master      ← Link
    │         └──── Commission Record  ← Created on enrollment
    │
    └──── Visa Application[]        ← Linked (1 application → 1 visa)

Sales Invoice (ERPNext Accounts)
    └──── Commission Record         ← Linked via invoice field
```

### Key Relationships
| From | To | Type | Notes |
|------|-----|------|-------|
| Student Profile | ERPNext Lead | Link | Created from CRM lead |
| Student Profile | ERPNext Customer | Link | Created when fee is invoiced |
| Student Application | Student Profile | Link | Many applications per student |
| Student Application | University Master | Link | One university per application |
| Visa Application | Student Application | Link | One visa per application |
| Commission Record | Sales Invoice | Link | For accounting |

---

## ⚙️ hooks.py Architecture

The `hooks.py` is the brain of eco_app. Key hooks to implement:

```python
# eco_app/eco_app/hooks.py

app_name = "eco_app"
app_title = "European Concept Overseas"
app_publisher = "European Concept Overseas"
app_description = "Study Abroad ERP"
app_color = "#1A3C6E"
app_icon = "graduation-cap"
app_version = "1.0.0"

# ── Document Events ──────────────────────────────────
doc_events = {
    "Student Profile": {
        "on_update": "eco_app.eco_app.events.student.on_update",
        "after_insert": "eco_app.eco_app.events.student.send_welcome_email",
    },
    "Student Application": {
        "on_update": "eco_app.eco_app.events.application.on_update",
        "on_submit": "eco_app.eco_app.events.application.on_submit",
    },
    "Lead": {
        "after_insert": "eco_app.eco_app.events.crm.sync_lead_to_student",
    }
}

# ── Scheduled Tasks ──────────────────────────────────
scheduler_events = {
    "daily": [
        "eco_app.eco_app.tasks.send_deadline_reminders",
        "eco_app.eco_app.tasks.check_visa_appointment_dates",
    ],
    "weekly": [
        "eco_app.eco_app.tasks.generate_weekly_report",
    ]
}

# ── Custom JS (loaded on all forms) ──────────────────
app_include_js = ["/assets/eco_app/js/eco_app.bundle.js"]
app_include_css = ["/assets/eco_app/css/eco_app.bundle.css"]

# ── Fixtures (data to export/import) ─────────────────
fixtures = [
    "Role",
    {"dt": "Custom Field", "filters": [["module", "=", "ECO App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "ECO App"]]},
    "Workflow",
    "Workflow State",
    "Workflow Action",
]
```

---

## 🔄 Workflow Architecture

### Student Journey Workflow (Frappe Workflow)
```
New Inquiry
    │ [Assign Counselor]
    ▼
Counseling
    │ [Request Documents]
    ▼
Documents Pending
    │ [Documents Verified]
    ▼
Applied
    │ [Offer Received]
    ▼
Offer Received
    │ [Student Accepts]
    ▼
Acceptance Confirmed
    │ [Apply for Visa]
    ▼
Visa Applied
    │ [Visa Decision]
    ├──[Approved]──► Visa Approved
    │                    │ [Enroll]
    │                    ▼
    │               Enrolled ✅
    │
    └──[Rejected]──► Visa Rejected ❌
                         │ [Re-counsel]
                         ▼
                    Counseling (loop back)
```

### Roles per Workflow Action
| Action | Allowed Roles |
|--------|--------------|
| Assign Counselor | ECO Manager |
| Request Documents | ECO Counselor, ECO Manager |
| Documents Verified | ECO Manager |
| Applied | ECO Counselor, ECO Manager |
| Offer Received | ECO Counselor, ECO Manager |
| Apply for Visa | ECO Visa Officer, ECO Manager |
| Visa Decision | ECO Visa Officer, ECO Manager |
| Enroll | ECO Manager |

---

## 🌍 Multi-Company Architecture

ECO may have multiple branches/offices in the future. Architecture must support:
- Every DocType has a `company` field linked to ERPNext `Company`
- All queries filter by `frappe.defaults.get_user_default("Company")`
- Reports support company filter
- Permissions scoped by company using User Permissions

---

## 🔐 Security Architecture

### Role Hierarchy
```
System Manager          ← Full system access (IT Admin only)
    │
ECO Manager             ← Full ECO access + accounts view
    │
    ├── ECO Counselor   ← Students, applications (no delete, no accounts)
    ├── ECO Accounts    ← Invoices, commissions (no student edit)
    └── ECO Visa Officer ← Visa applications only
    
ECO Student             ← Portal access — read own records only
```

### Permission Matrix
| DocType | ECO Manager | ECO Counselor | ECO Accounts | ECO Visa Officer | ECO Student |
|---------|------------|--------------|--------------|-----------------|-------------|
| Student Profile | CRUD | CRU | R | R | R (own) |
| Student Application | CRUD | CRU | R | R | R (own) |
| University Master | CRUD | R | R | R | - |
| Visa Application | CRUD | R | R | CRUD | R (own) |
| Commission Record | CRUD | - | CRUD | - | - |
| Sales Invoice | R | - | CRUD | - | - |

---

## 📦 Deployment Architecture

### Localhost (Development)
```
macOS
└── ~/eco-bench/
    ├── bench start          ← Starts all services
    ├── Redis (cache + queue)
    ├── MariaDB
    └── site: erp.eco.localhost:8000
```

### Production (Oracle Cloud Free Tier)
```
Oracle Cloud VM (Ubuntu 22.04, 4 OCPU, 24GB RAM)
├── Nginx (port 80/443, SSL via Let's Encrypt)
├── Supervisor (manages Gunicorn + workers)
├── Gunicorn (WSGI, 4 workers)
├── Redis (port 6379, local only)
├── MariaDB (port 3306, local only)
└── site: erp.europeanconcept.com
```

### Deployment Flow
```
macOS (dev) ──git push──► GitHub (eco_app repo)
                               │
                               │ SSH + bench get-app
                               ▼
                    Oracle Cloud VM
                    bench --site erp.europeanconcept.com migrate
                    bench build --app eco_app
                    sudo supervisorctl restart all
```

---

## 🔧 Configuration Architecture

### Site Config (never commit `site_config.json`)
```json
{
    "db_name": "eco_erp",
    "db_password": "NEVER_COMMIT_THIS",
    "maintenance_mode": 0,
    "pause_scheduler": 0,
    "max_file_size": 26214400
}
```

### App Config (safe to commit)
```python
# eco_app/eco_app/config/eco_app.py
data = {
    "label": "European Concept Overseas",
    "icon": "graduation-cap",
    "color": "#1A3C6E",
    "modules": [{"module_name": "ECO App", "label": "ECO App"}]
}
```

---

## 📌 Key Architectural Decisions (ADR Log)

| # | Decision | Reason | Date |
|---|----------|--------|------|
| 001 | Use ECO custom app, not ERPNext customization | Upgradability, clean separation | 2025 |
| 002 | MariaDB over PostgreSQL | Better ERPNext support, wider community | 2025 |
| 003 | Oracle Cloud Free Tier for production | Zero cost, 24GB RAM sufficient for ECO | 2025 |
| 004 | Single `ECO App` module (not split) | Simpler for small team, easy to navigate | 2025 |
| 005 | Frappe Workflows for student journey | Built-in email notifications, audit trail | 2025 |
| 006 | ERPNext CRM as lead source | Avoid duplicate lead management | 2025 |
| 007 | ERPNext Accounts for invoicing | Avoid rebuilding accounting from scratch | 2025 |
| 008 | GitHub private repo for eco_app | Version control + easy Oracle deployment | 2025 |

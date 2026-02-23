# 💻 Coding Standards — European Concept Overseas ERP
# eco_app | Frappe/ERPNext v17

---

## 🐍 Python Standards

### Version & Environment
- Python version: **3.11** (strict)
- Virtual environment: managed by `bench` — never activate manually
- Package installs: via `bench pip install <package>` only

### File Header (every .py file)
```python
# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani
```

### Imports Order
```python
# 1. Standard library
import os
import json
from datetime import datetime

# 2. Frappe
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, flt, cint

# 3. ERPNext
from erpnext.accounts.utils import get_balance_on

# 4. ECO App internal
from eco_app.eco_app.utils import get_student_stage
```

### Naming Conventions
| Type | Convention | Example |
|------|-----------|---------|
| Files | snake_case | `student_profile.py` |
| Classes | PascalCase | `StudentProfile` |
| Functions | snake_case | `get_application_status()` |
| Variables | snake_case | `student_name` |
| Constants | UPPER_SNAKE_CASE | `MAX_APPLICATIONS = 5` |
| DocType names | Title Case | `"Student Profile"` |

### Controller Class Rules
```python
from frappe.model.document import Document

class StudentProfile(Document):
    # Always define these hooks if needed
    def validate(self):
        self.validate_email()
        self.validate_passport()

    def before_save(self):
        self.set_full_name()

    def on_submit(self):
        self.create_application_record()

    def on_cancel(self):
        self.cancel_linked_applications()

    # Private methods use underscore prefix
    def _send_welcome_email(self):
        pass
```

### Frappe API — Always Use These

```python
# ✅ Correct — use Frappe ORM
doc = frappe.get_doc("Student Profile", name)
docs = frappe.get_list("Student Profile",
    filters={"status": "Active"},
    fields=["name", "full_name", "email"],
    order_by="creation desc",
    limit=20
)
value = frappe.db.get_value("Student Profile", name, "email")
frappe.db.set_value("Student Profile", name, "status", "Enrolled")

# ❌ Wrong — never raw SQL like this
frappe.db.sql("SELECT * FROM `tabStudent Profile` WHERE name = '%s'" % name)

# ✅ If raw SQL is absolutely unavoidable, use parameterized
frappe.db.sql("""
    SELECT name, full_name FROM `tabStudent Profile`
    WHERE status = %s AND company = %s
""", (status, company), as_dict=True)
```

### Error Handling
```python
# User-facing validation errors
frappe.throw(_("Passport number is required for visa application"))

# Non-blocking messages
frappe.msgprint(_("Application submitted successfully"), indicator="green")

# Logging (never use print())
frappe.logger("eco_app").info(f"Student {student_name} moved to Enrolled stage")
frappe.logger("eco_app").error(f"Failed to create invoice: {str(e)}")

# Permission check before sensitive operations
if not frappe.has_permission("Student Profile", "write", doc=doc):
    frappe.throw(_("You don't have permission to edit this record"), frappe.PermissionError)
```

### Whitelisted Methods (server API endpoints)
```python
@frappe.whitelist()
def get_student_applications(student):
    """Get all applications for a student — callable from client side"""
    frappe.has_permission("Student Application", "read", throw=True)
    return frappe.get_list("Student Application",
        filters={"student": student},
        fields=["name", "university", "status", "intake_month", "intake_year"]
    )

@frappe.whitelist()
def move_to_next_stage(student_profile):
    """Advance student to next application stage"""
    frappe.has_permission("Student Profile", "write", throw=True)
    doc = frappe.get_doc("Student Profile", student_profile)
    doc.advance_stage()
    doc.save()
    return doc.application_stage
```

---

## 🌐 JavaScript Standards

### File Header (every .js file)
```javascript
// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani
```

### Form Events Structure
```javascript
frappe.ui.form.on('Student Profile', {

    // Runs on every form load/refresh
    refresh(frm) {
        eco.setup_buttons(frm);
        eco.setup_indicators(frm);
    },

    // Runs when form first loads
    onload(frm) {
        eco.setup_filters(frm);
    },

    // Field-specific triggers (named after field)
    country_of_interest(frm) {
        frm.set_query('university', () => ({
            filters: { country: frm.doc.country_of_interest }
        }));
    },

    application_stage(frm) {
        eco.handle_stage_change(frm);
    }
});

// Namespace all custom functions under `eco` object
const eco = {
    setup_buttons(frm) {
        if (frm.doc.application_stage === 'Applied') {
            frm.add_custom_button(__('Mark Offer Received'), () => {
                eco.update_stage(frm, 'Offer Received');
            }, __('Actions'));
        }
    },

    update_stage(frm, stage) {
        frappe.confirm(`Move student to ${stage}?`, () => {
            frappe.call({
                method: 'eco_app.eco_app.doctype.student_profile.student_profile.move_to_next_stage',
                args: { student_profile: frm.doc.name, stage },
                callback(r) {
                    if (r.message) {
                        frm.reload_doc();
                        frappe.show_alert({ message: __('Stage updated'), indicator: 'green' });
                    }
                }
            });
        });
    }
};
```

### Frappe JS API — Always Use These
```javascript
// ✅ Server calls — always use frappe.call()
frappe.call({
    method: 'eco_app.eco_app.doctype.student_profile.student_profile.method_name',
    args: { name: frm.doc.name },
    freeze: true,                          // Freeze screen during call
    freeze_message: __('Processing...'),
    callback(r) {
        if (!r.exc && r.message) {
            // handle success
        }
    }
});

// ✅ Quick DB reads — frappe.db
frappe.db.get_value('University Master', university, 'commission_percent')
    .then(r => frm.set_value('commission', r.message.commission_percent));

// ✅ Navigation
frappe.set_route('Form', 'Student Application', application_name);
frappe.set_route('List', 'Student Profile', 'List');

// ✅ User feedback
frappe.show_alert({ message: __('Saved successfully'), indicator: 'green' });
frappe.confirm(__('Are you sure?'), () => { /* on yes */ });
frappe.msgprint(__('This action cannot be undone'));

// ❌ Never use raw fetch, jQuery.ajax, or XMLHttpRequest
```

### Naming Conventions (JS)
| Type | Convention | Example |
|------|-----------|---------|
| Variables | camelCase | `studentName` |
| Functions | camelCase | `getApplicationStatus()` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY = 3` |
| CSS classes | kebab-case | `eco-student-card` |

---

## 📋 DocType Standards

### Naming Series Format
```
ECO-STU-.YYYY.-.####    → Student Profile
ECO-APP-.YYYY.-.####    → Student Application
ECO-UNI-.####           → University Master
ECO-CRS-.####           → Course Master
ECO-VIS-.YYYY.-.####    → Visa Application
ECO-COM-.YYYY.-.####    → Commission Record
ECO-DOC-.YYYY.-.####    → Document Checklist
```

### Required Fields on Every DocType
```json
{ "fieldname": "naming_series", "fieldtype": "Data", "label": "Series" },
{ "fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Company" },
{ "fieldname": "status", "fieldtype": "Select", "label": "Status" },
{ "fieldname": "section_break_1", "fieldtype": "Section Break" }
```

### Field Type Reference
| Data Type | Frappe Field Type |
|-----------|-----------------|
| Short text | Data |
| Long text | Text / Small Text |
| Rich text | Text Editor |
| Number | Int / Float / Currency |
| Date | Date |
| Date + Time | Datetime |
| Yes/No | Check |
| Dropdown | Select |
| Link to another DocType | Link |
| Multiple links | Table MultiSelect |
| File upload | Attach / Attach Image |
| Read-only computed | Read Only |
| Password | Password |

### Child Table Rules
- Child DocType name: `<Parent> Item` (e.g., `Document Checklist Item`)
- Must have `parenttype`, `parent`, `parentfield` — auto-handled by Frappe
- Always set `"istable": 1` in DocType JSON
- Reference in parent using `"fieldtype": "Table"` and `"options": "Child DocType Name"`

---

## 🎨 CSS/SCSS Standards

```scss
// eco_app/public/css/eco_app.css

/* ECO Brand Variables */
:root {
    --eco-primary: #0B2E6B;      /* Deep Blue */
    --eco-secondary: #C62828;    /* Brand Red */
    --eco-success: #28A745;
    --eco-danger: #DC3545;
    --eco-light-bg: #F8F9FA;
}

/* Always namespace ECO custom styles */
.eco-student-card { }
.eco-stage-badge { }
.eco-dashboard-widget { }

/* Never override Frappe's core classes directly */
/* ❌ .form-control { } */
/* ✅ .eco-form .form-control { } */
```

---

## 📝 Code Review Checklist

Before every commit, verify:

- [ ] No modifications to `apps/erpnext/` or `apps/frappe/`
- [ ] All strings wrapped in `__()` for translation
- [ ] `frappe.has_permission()` on all whitelisted methods
- [ ] No raw SQL string formatting
- [ ] No `print()` statements — only `frappe.logger()`
- [ ] `bench migrate` run after schema changes
- [ ] `bench build --app eco_app` run after JS/CSS changes
- [ ] Fixtures exported if UI customizations were made
- [ ] Meaningful commit message following format: `feat|fix|chore: description`

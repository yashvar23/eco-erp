# 🧪 Testing Requirements — European Concept Overseas ERP
# eco_app | Frappe/ERPNext v17

---

## 🎯 Testing Philosophy

Every feature built for ECO ERP must be testable, tested, and verified before merging.
Tests protect the student data, application workflows, and financial records.

**Rule: No feature branch merges to `main` without passing tests.**

---

## 📁 Test File Structure

```
eco_app/
└── eco_app/
    └── tests/
        ├── __init__.py
        ├── test_student_profile.py
        ├── test_university_master.py
        ├── test_student_application.py
        ├── test_document_checklist.py
        ├── test_visa_application.py
        ├── test_commission_record.py
        └── utils/
            ├── __init__.py
            └── test_helpers.py          ← Shared test data factories
```

---

## 🏗️ Test File Template

Every test file must follow this structure:

```python
# Copyright (c) 2025, European Concept Overseas
# License: MIT

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase


class TestStudentProfile(FrappeTestCase):
    """Test cases for Student Profile DocType"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests in this class"""
        super().setUpClass()
        cls.create_test_dependencies()

    def setUp(self):
        """Run before each individual test"""
        frappe.set_user("Administrator")

    def tearDown(self):
        """Run after each individual test — clean up"""
        frappe.db.rollback()

    # ─────────────────────────────────────────
    # CREATION TESTS
    # ─────────────────────────────────────────

    def test_create_student_profile(self):
        """Test basic student profile creation"""
        student = self.make_student_profile()
        self.assertIsNotNone(student.name)
        self.assertEqual(student.application_stage, "New Inquiry")

    # ─────────────────────────────────────────
    # VALIDATION TESTS
    # ─────────────────────────────────────────

    def test_email_validation(self):
        """Test that invalid email raises error"""
        with self.assertRaises(frappe.ValidationError):
            self.make_student_profile(email="not-an-email")

    def test_passport_required_for_visa(self):
        """Test passport is mandatory before visa stage"""
        student = self.make_student_profile(passport_no=None)
        student.application_stage = "Visa Applied"
        with self.assertRaises(frappe.ValidationError):
            student.save()

    # ─────────────────────────────────────────
    # WORKFLOW TESTS
    # ─────────────────────────────────────────

    def test_stage_progression(self):
        """Test student moves through stages correctly"""
        student = self.make_student_profile()
        self.assertEqual(student.application_stage, "New Inquiry")

        student.application_stage = "Counseling"
        student.save()
        self.assertEqual(student.application_stage, "Counseling")

    def test_cannot_skip_stages(self):
        """Test student cannot skip required stages"""
        student = self.make_student_profile()
        student.application_stage = "Enrolled"   # Skip all stages
        with self.assertRaises(frappe.ValidationError):
            student.save()

    # ─────────────────────────────────────────
    # HELPER FACTORIES
    # ─────────────────────────────────────────

    @staticmethod
    def make_student_profile(**kwargs):
        """Factory to create a test student profile"""
        defaults = {
            "doctype": "Student Profile",
            "full_name": "Test Student",
            "email": "test.student@example.com",
            "mobile": "+91 9999999999",
            "passport_no": "A1234567",
            "country_of_interest": "Germany",
            "assigned_counselor": frappe.session.user,
            "date_of_inquiry": frappe.utils.nowdate(),
            "company": frappe.defaults.get_user_default("Company")
        }
        defaults.update(kwargs)
        doc = frappe.get_doc(defaults)
        doc.insert(ignore_permissions=True)
        return doc

    @classmethod
    def create_test_dependencies(cls):
        """Create any master data needed for tests"""
        pass
```

---

## ✅ Required Tests Per DocType

### Every DocType must have at minimum:

| Test Category | Required Tests |
|---|---|
| **Creation** | Create with valid data, verify naming series |
| **Validation** | Required fields, format validation, business rules |
| **Workflow** | Stage transitions, status changes |
| **Permissions** | Role-based access (ECO Counselor can't delete, etc.) |
| **Links** | Linked records update correctly |

---

## 📋 Test Coverage Per Module

### Student Profile ✅
- [ ] Create student with all required fields
- [ ] Email format validation
- [ ] Mobile number validation
- [ ] Passport required for visa-stage applications
- [ ] Duplicate email detection
- [ ] Stage progression (New Inquiry → Counseling → etc.)
- [ ] Cannot skip stages without required documents
- [ ] Assigned counselor receives notification on creation
- [ ] Permission: ECO Counselor can create, cannot delete

### University Master ✅
- [ ] Create university with required fields
- [ ] Duplicate university name in same country
- [ ] Commission percent between 0 and 100
- [ ] Intake months must have at least one entry

### Student Application ✅
- [ ] Link to valid Student Profile
- [ ] Link to valid University Master
- [ ] Intake date in future
- [ ] Status transitions
- [ ] Cannot have duplicate application (same student + university + intake)
- [ ] Commission record auto-created on enrollment

### Document Checklist ✅
- [ ] All required document types created per student
- [ ] Status changes tracked with timestamps
- [ ] Cannot proceed to "Applied" with pending mandatory documents
- [ ] File upload validation

### Visa Application ✅
- [ ] Linked student must have accepted offer
- [ ] Appointment date must be in future on creation
- [ ] Status: Approved triggers enrollment workflow
- [ ] Status: Rejected triggers counselor notification

### Commission Record ✅
- [ ] Amount matches university commission %
- [ ] Currency validation
- [ ] Linked to valid Sales Invoice
- [ ] Cannot create duplicate commission for same application

---

## 🏃 Running Tests

```bash
# Run all ECO app tests
bench --site erp.eco.localhost run-tests --app eco_app

# Run tests for a specific DocType
bench --site erp.eco.localhost run-tests \
    --module eco_app.eco_app.tests.test_student_profile

# Run a single test method
bench --site erp.eco.localhost run-tests \
    --module eco_app.eco_app.tests.test_student_profile \
    --test TestStudentProfile.test_stage_progression

# Run with verbose output
bench --site erp.eco.localhost run-tests --app eco_app --verbose

# Run with coverage report
bench --site erp.eco.localhost run-tests --app eco_app --coverage
```

---

## 🔍 Manual QA Checklist (Before Every Deployment)

Run these manually in browser before pushing to production:

### Student Workflow
- [ ] Create new student from CRM Lead
- [ ] Assign counselor and set country of interest
- [ ] Upload documents and verify checklist
- [ ] Create application for a university
- [ ] Move through all stages to Enrolled
- [ ] Verify commission record is auto-created

### Accounts
- [ ] Create service fee invoice for student
- [ ] Record payment received
- [ ] Create commission record from university

### Portal
- [ ] Student can login via portal
- [ ] Student can see their application status
- [ ] Student cannot see other students' data

### Reports
- [ ] Monthly Applications report loads correctly
- [ ] Counselor Performance report shows correct data
- [ ] Country-wise report filters work

---

## 🐛 Bug Report Format

When logging a bug in GitHub Issues, use this format:

```
**Module**: Student Profile
**Stage**: Production / Localhost
**Steps to Reproduce**:
1. Go to Student Profile
2. Set stage to Visa Applied without passport
3. Save

**Expected**: Validation error shown
**Actual**: Record saved without error

**ERPNext Version**: v17.x.x
**eco_app Commit**: abc1234
```

---

## 📊 Test Quality Standards

- Minimum **80% code coverage** for all new DocType controllers
- All `@frappe.whitelist()` methods must have at least one test
- All workflow transitions must have a passing test
- All validation rules must have a failing test (testing the error case)
- Tests must be **idempotent** — run multiple times with same result
- Tests must **not depend on each other** — each test is independent
- Use `frappe.db.rollback()` in tearDown to clean test data

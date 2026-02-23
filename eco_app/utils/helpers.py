# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

# 1. Standard library
from __future__ import annotations
from typing import Any

# 2. Frappe
import frappe
from frappe import _


def get_default_company() -> str:
    """Return the current user's default company."""
    return frappe.defaults.get_user_default("Company") or ""


def ensure_company_selected() -> str:
    """Ensure a default company is available for the current session."""
    company = get_default_company()
    if not company:
        frappe.throw(_("Please set a default Company before continuing."))
    return company


def as_dict(data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a safe dict placeholder for shared utility usage."""
    return dict(data or {})

# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe


def extend_bootinfo(bootinfo):
    """
    Frappe v16 boot hook.  Called once per login session to extend the
    bootinfo dict sent to the browser.

    This is the ONLY valid boot hook in Frappe v16.
    (boot_session was introduced in v17 — it is NOT used here.)
    """
    # ── ECO Branding ─────────────────────────────────────────────────────────
    bootinfo["app_logo_url"] = "/assets/eco_app/images/eco_logo.png"
    bootinfo["app_name"] = "ECO ERP"
    bootinfo["app_title"] = "European Concept Overseas"
    bootinfo["favicon"] = "/assets/eco_app/images/eco_favicon.ico"
    bootinfo["brand_html"] = (
        "<img src='/assets/eco_app/images/eco_logo.png' "
        "alt='European Concept Overseas' height='40'>"
    )

    # Remove default framework branding labels where present
    bootinfo.pop("frappe_version", None)
    bootinfo.pop("erpnext_version", None)

    # ── Module Filtering for ECO Users ───────────────────────────────────────
    # Merged from the former boot_session function (which is v17-only).
    # Only runs for sessions belonging to an ECO role — leaves System Manager
    # and other admin accounts untouched.
    user_roles = set(frappe.get_roles(frappe.session.user))
    eco_roles = {
        "ECO Manager",
        "ECO Counselor",
        "ECO Telecaller",
    }

    if not user_roles.intersection(eco_roles):
        return

    allowed_modules = {
        "Accounts",
        "CRM",
        "Projects",
        "Selling",
        "Support",
        "ECO App",
        "Setup",
        "ERPNext Settings",
    }

    blocked_modules = {
        "Assets",
        "Buying",
        "Manufacturing",
        "Quality Management",
        "Quality",
        "Stock",
        "Subcontracting",
    }

    def _is_permitted(module_name):
        return module_name in allowed_modules and module_name not in blocked_modules

    # Filter module list (Frappe v16 stores this in bootinfo["allowed_modules"])
    if isinstance(bootinfo.get("allowed_modules"), list):
        bootinfo["allowed_modules"] = [
            m for m in bootinfo["allowed_modules"] if _is_permitted(m)
        ]

    # Filter module page map
    if isinstance(bootinfo.get("module_page"), dict):
        bootinfo["module_page"] = {
            m: page
            for m, page in bootinfo["module_page"].items()
            if _is_permitted(m)
        }

    # Filter workspace list
    if isinstance(bootinfo.get("workspace"), list):
        bootinfo["workspace"] = [
            ws for ws in bootinfo["workspace"]
            if _is_permitted(
                ws.get("module") or ws.get("label") or ws.get("name", "")
            )
        ]

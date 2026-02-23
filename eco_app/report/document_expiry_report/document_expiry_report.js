// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.query_reports["Document Expiry Report"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            reqd: 1,
            default: frappe.defaults.get_user_default("Company"),
        },
        {
            fieldname: "days_range",
            label: __("Expiring Within (Days)"),
            fieldtype: "Select",
            options: "30\n60\n90\n180\nAll",
            default: "90",
        },
        {
            fieldname: "document_type",
            label: __("Document Type"),
            fieldtype: "Select",
            options:
                "\nPassport\nEnglish Test\nBank Statement\nPolice Clearance\nMedical Certificate",
        },
        {
            fieldname: "counselor",
            label: __("Counselor"),
            fieldtype: "Link",
            options: "User",
        },
    ],
};

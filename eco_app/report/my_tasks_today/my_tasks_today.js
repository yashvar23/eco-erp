// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.query_reports["My Tasks Today"] = {
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
            fieldname: "assigned_to",
            label: __("Assigned To"),
            fieldtype: "Link",
            options: "User",
            default: frappe.session.user,
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nOpen\nIn Progress\nCompleted\nCancelled",
            default: "Open",
        }
    ],
};

// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.query_reports["Fee Collection Report"] = {
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
            fieldname: "status",
            label: __("Current Status"),
            fieldtype: "Select",
            options: "\nActive\nFully Paid\nPartially Paid\nOverdue",
        },
        {
            fieldname: "counselor",
            label: __("Counselor"),
            fieldtype: "Link",
            options: "User",
        }
    ],
};

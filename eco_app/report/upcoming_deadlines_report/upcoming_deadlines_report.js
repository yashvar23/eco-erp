// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.query_reports["Upcoming Deadlines Report"] = {
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
            fieldname: "time_range",
            label: __("Time Range"),
            fieldtype: "Select",
            options: "\nNext 7 days\nNext 30 days\nNext 90 days",
            default: "Next 30 days",
        },
        {
            fieldname: "counselor",
            label: __("Counselor"),
            fieldtype: "Link",
            options: "User",
        },
    ],
};

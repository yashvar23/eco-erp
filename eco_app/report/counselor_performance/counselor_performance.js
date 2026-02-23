// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.query_reports["Counselor Performance"] = {
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
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end(),
        },
        {
            fieldname: "counselor",
            label: __("Counselor"),
            fieldtype: "Link",
            options: "User",
        },
        {
            fieldname: "stage",
            label: __("Stage"),
            fieldtype: "Select",
            options: "\nNew Inquiry\nCounseling\nDocuments Pending\nApplied\nOffer Received\nAcceptance Confirmed\nVisa Applied\nVisa Approved\nEnrolled\nClosed",
        },
    ],
};

// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Document Checklist Item", {
    form_render(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        if (row.status === "Verified" && !row.verified_on) {
            frappe.model.set_value(cdt, cdn, "verified_on", frappe.datetime.now_datetime());
        }

        if (row.status === "Submitted" && !row.submitted_on) {
            frappe.model.set_value(cdt, cdn, "submitted_on", frappe.datetime.now_datetime());
        }
    },
});

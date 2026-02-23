// Copyright (c) 2026, European Concept Overseas
// For license information, please see license.txt

frappe.ui.form.on("University Partnership", {
    refresh(frm) {
        if (frm.doc.status === "Expired") {
            frm.set_df_property('status', 'read_only', 1);
        }
    },
});

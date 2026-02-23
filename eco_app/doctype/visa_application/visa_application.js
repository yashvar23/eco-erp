// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Visa Application", {
    visa_status(frm) {
        const isTerminal = ["Approved", "Rejected", "Withdrawn"].includes(frm.doc.visa_status);
        frm.set_df_property("decision_date", "reqd", isTerminal ? 1 : 0);
        frm.set_df_property("rejection_reason", "reqd", frm.doc.visa_status === "Rejected" ? 1 : 0);
    },
});

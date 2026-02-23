// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Language Test Score", {
    refresh(frm) {
        // UI interactions
    },
    test_date(frm) {
        if (frm.doc.test_date) {
            const expiry = frappe.datetime.add_months(frm.doc.test_date, 24);
            frm.set_value("expiry_date", expiry);
        }
    },
    target_university(frm) {
        // Optional: We can fetch required_score live here or let backend set it
    }
});

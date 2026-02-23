// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("ECO Follow-up Task", {
    refresh(frm) {
        if (frm.doc.status === "Open" || frm.doc.status === "In Progress") {
            frm.add_custom_button(__("Mark Completed"), function () {
                frm.set_value("status", "Completed");
                frm.save();
            }).addClass("btn-primary");
        }
    },
});

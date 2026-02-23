// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Student Profile", {
    refresh(frm) {
        frm.set_intro(__("Central student record for counseling and application lifecycle."), "blue");

        frm.add_custom_button(__("Move to Next Stage"), () => {
            const nextStage = frm.doc.application_stage;

            frappe.call({
                method: "eco_app.eco_app.doctype.student_profile.student_profile.move_to_next_stage",
                args: {
                    student_profile: frm.doc.name,
                    stage: nextStage,
                },
                freeze: true,
                freeze_message: __("Updating student stage..."),
                callback(r) {
                    if (!r.exc) {
                        frm.reload_doc();
                        frappe.show_alert({ message: __("Stage updated"), indicator: "green" });
                    }
                },
            });
        }, __("Actions"));
    },
});

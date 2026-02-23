// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Student Application", {
    student_profile(frm) {
        if (!frm.doc.counselor && frm.doc.student_profile) {
            frappe.db.get_value("Student Profile", frm.doc.student_profile, "assigned_counselor").then((r) => {
                if (r.message && r.message.assigned_counselor) {
                    frm.set_value("counselor", r.message.assigned_counselor);
                }
            });
        }
    },

    scholarship_amount(frm) {
        eco.computeNetPayable(frm);
    },

    tuition_fee(frm) {
        eco.computeNetPayable(frm);
    },
});

const eco = {
    computeNetPayable(frm) {
        const tuition = flt(frm.doc.tuition_fee);
        const scholarship = flt(frm.doc.scholarship_amount);
        frm.set_value("net_payable", Math.max(tuition - scholarship, 0));
    },
};

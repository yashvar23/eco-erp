// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Commission Record", {
    commission_percent(frm) {
        eco.computeCommissionAmount(frm);
    },

    base_amount(frm) {
        eco.computeCommissionAmount(frm);
    },
});

const eco = {
    computeCommissionAmount(frm) {
        const percent = flt(frm.doc.commission_percent);
        const baseAmount = flt(frm.doc.base_amount);
        frm.set_value("commission_amount", (baseAmount * percent) / 100);
    },
};

// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

frappe.ui.form.on("Course Master", {
    refresh(frm) {
        frm.set_intro(__("Maintain courses linked to universities."), "blue");
    },
});

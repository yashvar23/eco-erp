// Copyright (c) 2026, European Concept Overseas
// License: Proprietary and Confidential. All rights reserved.
// Author: Yashvardhan Manghani

window.eco = window.eco || {};

window.eco.app = {
    version: "1.0.0",
    title: "ECO ERP",
};

window.eco.branding = {
    appName: "ECO ERP",
    companyName: "European Concept Overseas",
    primary: "#0B2E6B",
    secondary: "#C62828",
};

frappe.ready(() => {
    // Normalize page title
    const syncTitle = () => {
        if (!document.title || document.title.includes("Frappe") || document.title.includes("ERPNext")) {
            document.title = "ECO ERP";
        }
    };

    syncTitle();
    setTimeout(syncTitle, 300);
});

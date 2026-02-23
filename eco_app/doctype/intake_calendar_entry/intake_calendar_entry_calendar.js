frappe.views.calendar["Intake Calendar Entry"] = {
    field_map: {
        "start": "deadline_date",
        "end": "deadline_date",
        "id": "name",
        "title": "title",
        "allDay": "allDay"
    },
    style_map: {
        "Visa Deadline": "danger",
        "Application Deadline": "info",
        "Intake Start": "success",
        "Scholarship Deadline": "warning",
        "Document Deadline": "primary",
        "Appointment": "dark",
        "Other": "secondary"
    },
    order_by: "deadline_date",
    get_events_method: "frappe.desk.calendar.get_events",
    filters: [
        {
            "fieldtype": "Link",
            "fieldname": "linked_student",
            "options": "Student Profile",
            "label": __("Student")
        },
        {
            "fieldtype": "Select",
            "fieldname": "entry_type",
            "options": "\nApplication Deadline\nIntake Start\nVisa Deadline\nScholarship Deadline\nDocument Deadline\nAppointment\nOther",
            "label": __("Entry Type")
        }
    ]
};

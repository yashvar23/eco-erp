# Copyright (c) 2026, European Concept Overseas
# License: Proprietary and Confidential. All rights reserved.
# Author: Yashvardhan Manghani

import frappe
from frappe import _
from frappe.model.document import Document


class CourseMaster(Document):
    def autoname(self):
        self.name = frappe.model.naming.make_autoname("ECO-CRS-.####")

    def validate(self):
        self._set_defaults()
        self._validate_duration_months()
        self._validate_duplicate_course_per_university()

    def _set_defaults(self):
        if not self.naming_series:
            self.naming_series = "ECO-CRS-.####"

    def _validate_duration_months(self):
        if self.duration_months is None or self.duration_months <= 0:
            frappe.throw(_("Duration (Months) must be greater than 0."))

    def _validate_duplicate_course_per_university(self):
        duplicate = frappe.db.exists(
            "Course Master",
            {
                "name": ["!=", self.name],
                "university": self.university,
                "course_name": self.course_name,
                "course_level": self.course_level,
            },
        )
        if duplicate:
            frappe.throw(
                _("Course {0} already exists for university {1}.").format(
                    self.course_name, self.university
                )
            )

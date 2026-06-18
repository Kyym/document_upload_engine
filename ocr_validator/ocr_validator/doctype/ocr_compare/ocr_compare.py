# Copyright (c) 2026, CCI Global and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OCRCompare(Document):
    def validate(self):
        if not self.must_have_table:
            frappe.throw("At least one Must Have rule is required.")

        # Ensure OR rule groups have at least two entries per group
        groups: dict[str, int] = {}
        for row in self.or_table:
            groups[row.group_name] = groups.get(row.group_name, 0) + 1
        for group, count in groups.items():
            if count < 2:
                frappe.msgprint(
                    f"OR Rule group '{group}' has only one entry – "
                    "consider adding more alternatives or moving it to Must Have.",
                    indicator="orange",
                    alert=True,
                )

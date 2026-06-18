// Copyright (c) 2026, CCI Global and contributors
// For license information, please see license.txt

frappe.ui.form.on("OCR Compare", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Open Validator"), function () {
				window.open("/ocr-validator", "_blank");
			}, __("Tools"));

			frm.add_custom_button(__("Test This Config"), function () {
				const url =
					"/ocr-validator?doc_type=" +
					encodeURIComponent(frm.doc.document_type) +
					"&country=" +
					encodeURIComponent(frm.doc.country);
				window.open(url, "_blank");
			}, __("Tools"));
		}
	},

	document_type(frm) {
		if (frm.doc.document_type && frm.doc.country) {
			frm.set_value(
				"autoname",
				frm.doc.document_type + "-" + frm.doc.country
			);
		}
	},
});

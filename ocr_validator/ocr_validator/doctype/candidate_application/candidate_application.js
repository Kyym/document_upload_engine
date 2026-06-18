// Copyright (c) 2026, CCI Global and contributors
// For license information, please see license.txt

frappe.ui.form.on("Candidate Application", {
	refresh(frm) {
		// Show "Generate Portal Link" button always (saved doc)
		if (!frm.is_new()) {
			frm.add_custom_button(__("Generate Portal Link"), function () {
				frappe.confirm(
					`Generate a new portal link for <b>${frm.doc.full_name}</b> and send it to <b>${frm.doc.email}</b>?`,
					function () {
						frappe.show_alert({ message: "Generating link…", indicator: "blue" });
						frappe.call({
							method: "ocr_validator.ocr_validator.doctype.candidate_application.candidate_application.generate_and_send_portal_link",
							args: { application_name: frm.doc.name },
							callback(r) {
								if (r.message && r.message.portal_url) {
									frm.reload_doc();
									frappe.show_alert({
										message: `✅ Link generated and emailed to ${frm.doc.email}`,
										indicator: "green"
									}, 6);
									// Also show a dialog with the link for immediate copy
									let d = new frappe.ui.Dialog({
										title: "Portal Link Generated",
										fields: [
											{
												fieldtype: "HTML",
												options: `
												<div style="padding:12px 0">
												<p style="margin-bottom:10px;font-size:13px;color:#6b7280">
													The link below has been emailed to <strong>${frm.doc.email}</strong>.
													You can also copy and share it directly.
												</p>
												<div style="display:flex;gap:8px;align-items:center">
													<input id="portal-link-input" type="text"
														value="${r.message.portal_url}"
														readonly
														style="flex:1;padding:8px 12px;border:1px solid #d1d5db;
														border-radius:6px;font-size:13px;background:#f9fafb;color:#111827">
													<button onclick="
														var el=document.getElementById('portal-link-input');
														el.select();navigator.clipboard.writeText(el.value);
														this.textContent='Copied!';this.style.background='#16a34a';
														setTimeout(()=>{this.textContent='Copy';this.style.background='#050b34'},2000)
													" style="padding:8px 18px;background:#050b34;color:white;
													border:none;border-radius:6px;cursor:pointer;font-weight:600;
													font-size:13px;white-space:nowrap">Copy</button>
												</div>
												<p style="margin-top:10px;font-size:12px;color:#9ca3af">
													🔒 This is a secure one-time link. Generating a new link will invalidate the previous one.
												</p>
												</div>`
											}
										],
										primary_action_label: "Close",
										primary_action() { d.hide(); }
									});
									d.show();
								}
							}
						});
					}
				);
			}, __("Actions"));

			// If portal_url exists, show it inline as a clickable link
			if (frm.doc.portal_url) {
				frm.get_field("portal_url").$wrapper.find(".control-value").html(
					`<a href="${frm.doc.portal_url}" target="_blank" style="color:#0a1560;font-weight:500">
						🔗 ${frm.doc.portal_url}
					</a>`
				);
			}
		}
	}
});

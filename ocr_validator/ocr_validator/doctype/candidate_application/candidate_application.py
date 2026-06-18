# Copyright (c) 2026, CCI Global and contributors
# For license information, please see license.txt

import secrets
import frappe
from frappe import _
from frappe.model.document import Document


class CandidateApplication(Document):
    pass


@frappe.whitelist()
def generate_and_send_portal_link(application_name):
    """
    Generate a submission token, persist it + the portal URL on the
    Candidate Application, send an email to the candidate, and return
    the portal URL so the JS can display it immediately.
    """
    app = frappe.get_doc("Candidate Application", application_name)

    if not app.email:
        frappe.throw(_("Please add an email address to the application before generating a portal link."))

    # Generate a secure token
    token = secrets.token_urlsafe(32)
    base_url = frappe.utils.get_url()
    portal_url = f"{base_url}/document-upload?token={token}"

    # Persist token + URL (works whether doc is saved or submitted)
    frappe.db.set_value("Candidate Application", application_name, {
        "submission_token": token,
        "portal_url": portal_url,
    })
    frappe.db.commit()

    # Send email
    _send_portal_email(app, portal_url)

    return {"token": token, "portal_url": portal_url}


def _send_portal_email(app, portal_url):
    """Send the portal link email to the candidate."""
    subject = f"CCI Global — Document Submission Portal: {app.document_bundle}"

    message = f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;color:#0d1240">

      <!-- Header -->
      <div style="background:#050b34;padding:24px 32px;border-bottom:3px solid #ea781b">
        <table cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding-right:10px">
              <!-- CCI bars -->
              <div style="width:22px;border-top:3.5px solid #b8b8b8;margin-bottom:4px"></div>
              <div style="width:22px;border-top:3.5px solid #b8b8b8"></div>
            </td>
            <td>
              <span style="font-family:'Arial Black',Arial,sans-serif;font-size:22px;
                font-weight:900;color:#b8b8b8;letter-spacing:3px">CCI</span>
              <span style="display:block;font-size:10px;color:#6786ac;
                letter-spacing:4px;text-transform:uppercase">GLOBAL</span>
            </td>
          </tr>
        </table>
      </div>

      <!-- Body -->
      <div style="padding:32px;background:#ffffff;border:1px solid #e5e7eb">
        <p style="font-size:16px;font-weight:600;margin-bottom:8px">
          Hello {app.full_name},
        </p>
        <p style="font-size:14px;color:#4b5563;margin-bottom:20px;line-height:1.6">
          You have been invited to submit your documents for the
          <strong>{app.document_bundle}</strong> application via the
          CCI Global secure document portal.
        </p>

        <!-- CTA Button -->
        <div style="text-align:center;margin:28px 0">
          <a href="{portal_url}"
             style="background:#ea781b;color:#ffffff;padding:14px 36px;
             font-size:15px;font-weight:700;text-decoration:none;
             letter-spacing:1px;text-transform:uppercase;display:inline-block">
            OPEN DOCUMENT PORTAL →
          </a>
        </div>

        <p style="font-size:13px;color:#6b7280;margin-bottom:6px">
          Or copy this link into your browser:
        </p>
        <p style="font-size:12px;background:#f3f4f6;padding:10px 14px;
          border-left:3px solid #ea781b;word-break:break-all;color:#374151">
          {portal_url}
        </p>

        <!-- Instructions -->
        <div style="margin-top:24px;padding:16px;background:#f9fafb;
          border:1px solid #e5e7eb;border-radius:4px">
          <p style="font-size:13px;font-weight:700;color:#050b34;margin-bottom:8px">
            What you need to do:
          </p>
          <ol style="font-size:13px;color:#4b5563;padding-left:18px;line-height:1.8;margin:0">
            <li>Click the button above to open the secure portal</li>
            <li>Select each document type and upload the required file</li>
            <li>Wait for OCR validation to confirm each document</li>
            <li>Once all documents are verified you will be notified</li>
          </ol>
        </div>

        <p style="font-size:12px;color:#9ca3af;margin-top:24px;border-top:1px solid #f3f4f6;
          padding-top:16px;line-height:1.6">
          🔒 This is a secure, personalised link. Please do not share it with others.
          If you did not expect this email, please ignore it or contact us at
          <a href="mailto:support@cciglobal.com" style="color:#6786ac">support@cciglobal.com</a>.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f3f4f6;padding:16px 32px;
        font-size:11px;color:#9ca3af;text-align:center">
        © 2025 CCI Global. All rights reserved. &nbsp;|&nbsp;
        <a href="#" style="color:#6786ac;text-decoration:none">Privacy Policy</a> &nbsp;|&nbsp;
        <a href="#" style="color:#6786ac;text-decoration:none">Help Center</a>
      </div>

    </div>
    """

    frappe.sendmail(
        recipients=[app.email],
        subject=subject,
        message=message,
        now=True,
    )

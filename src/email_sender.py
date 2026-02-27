"""Email delivery for legal digest using Resend API."""
import os
from typing import Optional

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailSender:
    """Sends digest emails via Resend API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize email sender.

        Args:
            api_key: Resend API key. Falls back to RESEND_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get('RESEND_API_KEY')
        self.enabled = bool(self.api_key) and RESEND_AVAILABLE

        if not RESEND_AVAILABLE:
            print("  [EmailSender] resend package not installed. Run: pip install resend")
        elif not self.api_key:
            print("  [EmailSender] No API key found. Set RESEND_API_KEY env var.")

        if self.enabled:
            resend.api_key = self.api_key

    def send_digest(self, html_content: str, subject: str, to_email: str,
                    from_email: str = "onboarding@resend.dev") -> bool:
        """
        Send digest email.

        Args:
            html_content: HTML body of the email
            subject: Email subject line
            to_email: Recipient email address
            from_email: Sender email address

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            print("  [EmailSender] Email delivery disabled — missing API key or resend package")
            return False

        email_html = self._wrap_in_email_template(html_content, subject)

        try:
            params = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": email_html,
            }
            result = resend.Emails.send(params)
            print(f"  [EmailSender] Email sent successfully (id: {result.get('id', 'unknown')})")
            return True
        except Exception as e:
            print(f"  [EmailSender] Failed to send email: {e}")
            return False

    def _wrap_in_email_template(self, content: str, subject: str) -> str:
        """Wrap RSS content:encoded HTML in an email-safe template."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 680px; margin: 0 auto; background: #ffffff;">
    <tr>
      <td style="padding: 32px 24px 16px; background: #1a1a2e; color: #ffffff;">
        <h1 style="margin: 0; font-size: 22px; font-weight: 600;">{subject}</h1>
        <p style="margin: 8px 0 0; font-size: 14px; color: #a0a0b0;">APAC Legal Digest — Weekly Briefing</p>
      </td>
    </tr>
    <tr>
      <td style="padding: 24px;">
        {content}
      </td>
    </tr>
    <tr>
      <td style="padding: 16px 24px; background: #f0f0f5; font-size: 12px; color: #666;">
        <p style="margin: 0;">This digest is auto-generated. Verify all information with primary sources.</p>
      </td>
    </tr>
  </table>
</body>
</html>"""

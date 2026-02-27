#!/usr/bin/env python3
"""Send the generated digest via email."""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_sender import EmailSender
from src.date_utils import get_last_week_range, format_date_range


def main():
    to_email = os.environ.get('DIGEST_EMAIL', '')
    if not to_email:
        print("DIGEST_EMAIL not set — skipping email")
        return

    start, end = get_last_week_range()
    subject = f"APAC Legal Digest - Week of {format_date_range(start, end)}"

    feed_file = Path(__file__).parent.parent / 'docs' / 'feed.xml'
    if not feed_file.exists():
        print("No feed.xml found — skipping email")
        return

    content = feed_file.read_text()
    sender = EmailSender()
    sender.send_digest(content, subject, to_email)


if __name__ == '__main__':
    main()

"""Date calculation utilities for the digest generator."""
from datetime import datetime, timedelta


def get_last_week_range():
    """
    Calculate the most recent Monday-Sunday period ending yesterday.

    Returns:
        tuple: (start_date, end_date) as datetime objects for the week range
    """
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Find the most recent Sunday (end of week)
    days_since_sunday = (yesterday.weekday() + 1) % 7
    if days_since_sunday == 0 and yesterday.weekday() == 6:
        # Yesterday was Sunday
        end_date = yesterday
    else:
        # Go back to the most recent Sunday
        end_date = yesterday - timedelta(days=days_since_sunday)

    # Monday is 6 days before Sunday
    start_date = end_date - timedelta(days=6)

    return start_date, end_date


def format_date_range(start_date, end_date):
    """
    Format date range for digest title.

    Args:
        start_date: datetime object
        end_date: datetime object

    Returns:
        str: Formatted date range (e.g., "15 December 2024")
    """
    return end_date.strftime("%d %B %Y")


def format_source_date(date_obj):
    """
    Format date for source citation.

    Args:
        date_obj: datetime object

    Returns:
        str: Formatted date (e.g., "15 Dec")
    """
    return date_obj.strftime("%d %b")


def is_date_in_range(date_str, start_date, end_date):
    """
    Check if a date string falls within the target week.

    Args:
        date_str: String date in various formats
        start_date: datetime object
        end_date: datetime object

    Returns:
        bool: True if date is in range
    """
    try:
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y/%m/%d",
            "%d/%m/%Y"
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                return start_date <= parsed_date <= end_date
            except ValueError:
                continue

        return False
    except Exception:
        return False


def get_week_description(start_date, end_date):
    """
    Get a human-readable week description.

    Args:
        start_date: datetime object
        end_date: datetime object

    Returns:
        str: Week description
    """
    return f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"

import frappe
import pytz
import re
from datetime import datetime

@staticmethod
def standardize_phone_number(number: str) -> str:
    """Standardizes a phone number.

    Args:
        number (str): Phone number to standardize

    Returns:
        str: Standardized phone number
    """
    if not number:
        return None
    
    config = frappe.get_single("Weclapp Migration Settings")

    # Remove all non-numeric characters
    cleaned_number = re.sub(r'\D', '', number)

    # Check if there is already a country code
    # If not, add the default one
    if cleaned_number.startswith('00'):
        cleaned_number = f"+{cleaned_number[2:]}"
    elif cleaned_number.startswith('0'):
        cleaned_number = f"+{config.default_phone_country_code}{cleaned_number[1:]}"
    elif cleaned_number:
        cleaned_number = f"+{cleaned_number}"

    # Insert dash (-) after the country code
    if len(cleaned_number) > 3:
        cleaned_number = f"{cleaned_number[:3]}-{cleaned_number[3:]}"

    return cleaned_number

@staticmethod
def remove_html_tags(text: str) -> str:
    """Removes all HTML tags from the given text.

    Args:
        text (str): Text to remove the HTML tags from

    Returns:
        str: Text without HTML tags
    """
    return re.sub(r'&[^;]+;', '', re.sub(r'<[^>]*>', '', text)) if text else None

@staticmethod
def get_country_by_code(code: str) -> str:
    """Returns the country name for the given country code.

    Args:
        code (str): Country code to get the country name for

    Returns:
        str: Country name
    """
    country = frappe.get_all("Country", filters={"code": code.lower()}, fields=["name"])
    return country[0].get("name", None) if len(country) > 0 else None

@staticmethod
def get_salutation(wc_salutation: str, wc_title: str) -> str:
    """Returns the salutation for the given salutation and title.
    If a title is given, the salutation will be ignored.

    Args:
        wc_salutation (str): Salutation from Weclapp
        wc_title (str): Title from Weclapp

    Returns:
        str: Salutation
    """
    if wc_title:
        return wc_title
    elif wc_salutation == "MR":
        return "Mr"
    elif wc_salutation == "MRS":
        return "Ms"

@staticmethod
def prepare_email(email: str) -> str:
    """Prepares the email address for the given email.
    Replace umlauts and check if the email address is valid.
    Returns None if the email address is invalid.

    Args:
        email (str): Email address to prepare

    Returns:
        str: Prepared email address
    """
    if not email:
        return None
    email = email.lower().replace("ä", "ae") \
                            .replace("ö", "oe") \
                            .replace("ü", "ue") \
                            .replace("ß", "ss")
    return email if re.match(r"^\S+@\S+\.\S+$", email) else None

@staticmethod
def get_date_from_weclapp_ts(timestamp: int) -> str:
    """Returns a date string from a WeClapp timestamp.

    Args:
        timestamp (int): WeClapp timestamp

    Returns:
        str: Date string
    """
    if not timestamp:
        return None
    system_timezone = frappe.db.get_single_value('System Settings', 'time_zone')
    return datetime.fromtimestamp(timestamp / 1000, pytz.timezone(system_timezone)).strftime("%Y-%m-%d")

@staticmethod
def get_datetime_from_weclapp_ts(timestamp: int) -> str:
    """Returns a datetime string from a WeClapp timestamp.

    Args:
        timestamp (int): WeClapp timestamp

    Returns:
        str: Datetime string
    """
    if not timestamp:
        return None
    system_timezone = frappe.db.get_single_value('System Settings', 'time_zone')
    return datetime.fromtimestamp(timestamp / 1000, pytz.timezone(system_timezone)).strftime("%Y-%m-%d %H:%M:%S")
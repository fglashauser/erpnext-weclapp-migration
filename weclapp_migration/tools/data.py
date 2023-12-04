import frappe
import re

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
    return re.sub(r'<[^>]*>', '', text) if text else None

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
    
def get_tags(wc_tags: list, wc_topics: list) -> str:
    """Returns the tags for the given tags and topics.

    Args:
        wc_tags (list): Tags from Weclapp
        wc_topics (list): Topics from Weclapp

    Returns:
        str: Tags
    """
    tags = list()
    if wc_tags:
        tags += wc_tags
    if wc_topics:
        tags += [x["name"] for x in wc_topics]
    return ",".join(tags)
import frappe
from .migration import Migration
from ..tools.data import get_country_by_code, standardize_phone_number

class AddressMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return None

    @property
    def en_doctype(self) -> str:
        return "Address"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"                 : wc_obj.get("id", None),
            "address_title"         : self.parent_doc.name,
            "city"                  : wc_obj.get("city", None),
            "country"               : get_country_by_code(wc_obj.get("countryCode", None)),
            "address_type"          : self._address_type(wc_obj),
            "is_shipping_address"   : wc_obj.get("deliveryAddress", False),
            "is_primary_address"    : wc_obj.get("primeAddress", False) or wc_obj.get("invoiceAddress", False),
            "phone"                 : standardize_phone_number(wc_obj.get("phoneNumber", None)),
            "state"                 : wc_obj.get("state", None),
            "address_line1"         : wc_obj.get("street1", None),
            "address_line2"         : wc_obj.get("street2", None),
            "pincode"               : wc_obj.get("zipcode", None)
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        pass
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        pass

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj

    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        pass

    def _address_type(self, wc_obj: dict) -> str:
        if wc_obj.get("invoiceAddress", False) or wc_obj.get("primeAddress", False):
            return "Billing"
        elif wc_obj.get("deliveryAddress", False):
            return "Shipping"
        elif self.parent_doc.doctype == "Contact":
            return "Personal"
        else:
            return "Other"
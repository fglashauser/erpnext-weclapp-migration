import frappe
from .migration import Migration
from ..tools.data import get_country_by_code, standardize_phone_number

class ExtendedContractMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "contract"

    @property
    def en_doctype(self) -> str:
        return "Extended Contract"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"                 : wc_obj.get("id", None),
            # TODO: Add more fields
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        pass
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        pass

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj

    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        pass
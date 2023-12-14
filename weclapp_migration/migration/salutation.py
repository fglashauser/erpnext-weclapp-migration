import frappe
from .migration import Migration

class SalutationMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "title"

    @property
    def en_doctype(self) -> str:
        return "Salutation"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"         : wc_obj.get("id", None),
            "salutation"    : wc_obj.get("name", None),
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        pass
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        pass

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj
    
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        pass
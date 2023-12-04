import frappe
from .migration import Migration

class LeadSourceMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "leadSource"

    @property
    def en_doctype(self) -> str:
        return "Lead Source"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"         : wc_obj.get("id", None),
            "source_name"   : wc_obj.get("name", None)
        }
    
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        """Executes after the migration of an entity"""
        pass
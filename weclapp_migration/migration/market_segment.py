import frappe
from .migration import Migration

class MarketSegmentMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "customerCategory"

    @property
    def en_doctype(self) -> str:
        return "Market Segment"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"             : wc_obj.get("id", None),
            "market_segment"    : wc_obj.get("name", None)
        }
    
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        """Executes after the migration of an entity"""
        pass
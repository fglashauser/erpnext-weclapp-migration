import frappe
from .migration import Migration

class ItemMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "article"

    @property
    def en_doctype(self) -> str:
        return "Item"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"         : wc_obj.get("id", None),
            "item_group"    : "Products",
            "is_stock_item" : False,
            "item_code"     : wc_obj.get("articleNumber", None),
            "item_name"     : wc_obj.get("name", None),
            "stock_uom"     : wc_obj.get("unitName", None),
            "description"   : wc_obj.get("description", None),
            "standard_rate" : self._sale_price(wc_obj)
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        pass
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        pass

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj

    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        pass

    def _sale_price(self, wc_obj: dict) -> float:
        price = next(iter(wc_obj.get("articlePrices", list())[::-1]), None)
        return price.get("price", 0.0) if price else 0.0
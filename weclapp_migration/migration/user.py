import frappe
from .migration import Migration
from ..tools.data import prepare_email

class UserMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "user"

    @property
    def en_doctype(self) -> str:
        return "User"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "email"         : prepare_email(wc_obj.get("email", None)),
            "first_name"    : wc_obj.get("firstName", None),
            "last_name"     : wc_obj.get("lastName", None),
            "language"      : self.api.config.default_language
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        pass
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        pass

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj

    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        pass
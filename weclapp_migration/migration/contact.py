import frappe
from .migration import Migration
from .address import AddressMigration
from ..tools.data import standardize_phone_number, get_salutation

class ContactMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return None

    @property
    def en_doctype(self) -> str:
        return "Contact"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"             : wc_obj.get("id", None),
            "salutation"        : get_salutation(wc_obj.get("salutation", None), wc_obj.get("title", None)),
            "first_name"        : wc_obj.get("firstName", None),
            "last_name"         : wc_obj.get("lastName", None),
            "email_ids"         : self._email_ids(wc_obj),
            "phone_nos"         : self._phone_nos(wc_obj),
        }
    
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        addr = wc_obj.get("addresses", list())
        if len(addr) == 0:
            return
        en_doc.update({
            "address": self._migrate_linked_docs(AddressMigration(parent_doc=en_doc), en_doc, addr)[0].name
        }).save()

    def _email_ids(self, wc_obj: dict) -> list:
        email = wc_obj.get("email", None)
        return [{"email_id": email, "is_primary": True}] if email else list()

    def _phone_nos(self, wc_obj: dict) -> list:
        phone_nos = list()
        phone = wc_obj.get("phone", None)
        fax = wc_obj.get("fax", None)
        mobilePhone1 = wc_obj.get("mobilePhone1", None)
        mobilePhone2 = wc_obj.get("mobilePhone2", None)
        if phone:
            phone_nos.append({"phone": standardize_phone_number(phone), "is_primary_phone": True})
        if fax:
            phone_nos.append({"phone": standardize_phone_number(fax), "custom_is_fax_number": True})
        if mobilePhone1:
            phone_nos.append({"phone": standardize_phone_number(mobilePhone1), "is_primary_mobile_no": True})
        if mobilePhone2:
            phone_nos.append({"phone": standardize_phone_number(mobilePhone2)})
        return phone_nos
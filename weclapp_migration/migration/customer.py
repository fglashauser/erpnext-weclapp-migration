import frappe
from .migration import Migration
from ..tools.data import standardize_phone_number, remove_html_tags, get_salutation, prepare_email
from .contact import ContactMigration
from .address import AddressMigration

class CustomerMigration(Migration):
    """Migrates customers from WeClapp to ERPNext"""

    @property
    def wc_doctype(self) -> str:
        return "customer"

    @property
    def en_doctype(self) -> str:
        return "Customer"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        try:
            account_manager = frappe.get_doc("User", wc_obj.get("responsibleUserUsername", None))
        except frappe.exceptions.DoesNotExistError as e:
            account_manager = None
        return {
            "wc_id"                         : wc_obj.get("id", None),
            "name"                          : wc_obj.get("customerNumber", None),
            "salutation"                    : get_salutation(wc_obj.get("salutation", None), wc_obj.get("title", None)),
            "customer_name"                 : self._customer_name(wc_obj),
            "customer_type"                 : self._customer_type(wc_obj),
            "website"                       : wc_obj.get("website", None),
            "tax_id"                        : wc_obj.get("vatRegistrationNumber", None),
            "phone"                         : standardize_phone_number(wc_obj.get("phone", str())),
            "email"                         : prepare_email(wc_obj.get("email", None)),
            "industry"                      : wc_obj.get("sectorName", None),
            "market_segment"                : wc_obj.get("customerCategoryName", None),
            "rating"                        : wc_obj.get("customerRatingName", None),
            "lead_source"                   : wc_obj.get("leadSourceName", None),
            "customer_details"              : self._customer_details(wc_obj),
            "customer_group"                : self.api.config.default_customer_group,
            "territory"                     : self.api.config.default_territory,
            "account_manager"               : account_manager.name if \
                account_manager and account_manager.name != wc_obj.get("email", None) \
                else None
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        return wc_obj.get("customerTopics", list())
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        en_doc.reload()
        en_doc.update({
            "customer_primary_contact": None,
            "customer_primary_address": None
        }).save()
        frappe.db.commit()
        en_doc.reload()
        self._delete_linked_childs(ContactMigration(self.api, parent_doc=en_doc), en_doc)
        self._delete_linked_childs(AddressMigration(self.api, parent_doc=en_doc), en_doc)

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj
    
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        # Contacts
        contactMigration = ContactMigration(self.api, parent_doc=en_doc)
        self._migrate_linked_docs(contactMigration, en_doc, wc_obj.get("contacts", list()))
        en_doc.reload()
        primary_contact = contactMigration.get_doc_by_wc_id(wc_obj.get("primaryContactId", None))
        if primary_contact:
            en_doc.update({
                "customer_primary_contact": primary_contact.name
            }).save()
            primary_contact.update({
                "is_primary_contact": True
            }).save()
        # Addresses
        addrMigration = AddressMigration(self.api, parent_doc=en_doc)
        self._migrate_linked_docs(addrMigration, en_doc, wc_obj.get("addresses", list()))
        en_doc.reload()
        primary_address = addrMigration.get_doc_by_wc_id(wc_obj.get("primaryAddressId", None))
        if primary_address:
            en_doc.update({
                "customer_primary_address": primary_address.name
            }).save()
            primary_address.update({
                "is_primary_address": True
            }).save()

    def _is_company(self, wc_obj: dict) -> bool:
        return wc_obj.get("partyType", None) != "PERSON"
    
    def _customer_name(self, wc_obj: dict) -> str:
        return wc_obj.get("company", str()) if self._is_company(wc_obj) else \
            f"{wc_obj.get('firstName', str())} {wc_obj.get('lastName', str())}".strip()
    
    def _customer_type(self, wc_obj: dict) -> str:
        return "Company" if self._is_company(wc_obj) else "Individual"
    
    def _customer_details(self, wc_obj: dict) -> str:
        details = str()
        # Description
        if wc_obj.get("description", None):
            details += wc_obj.get('description', None)
        # Notes
        parties = self.api.get_cache_objects("party", query=lambda x: x["customerNumber"] == wc_obj["customerNumber"])
        for party in parties:
            if party.get("customerInternalNote", None):
                if len(details) > 0:
                    details += "\n\n-------------------------\n\n"
                details += party.get("customerInternalNote", None)
        return remove_html_tags(details)
    
    
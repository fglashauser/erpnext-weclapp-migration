import frappe
from .migration import Migration
from ..tools.data import standardize_phone_number, remove_html_tags, get_salutation, get_tags
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
        return {
            "wc_id"                         : wc_obj.get("id", None),
            "name"                          : wc_obj.get("customerNumber", None),
            "salutation"                    : get_salutation(wc_obj.get("salutation", None), wc_obj.get("title", None)),
            "customer_name"                 : self._customer_name(wc_obj),
            "customer_type"                 : self._customer_type(wc_obj),
            "website"                       : wc_obj.get("website", None),
            "tax_id"                        : wc_obj.get("vatRegistrationNumber", None),
            "custom_phone"                  : standardize_phone_number(wc_obj.get("phone", str())),
            "custom_email"                  : wc_obj.get("email", None),
            "industry"                      : wc_obj.get("sectorName", None),
            "market_segment"                : wc_obj.get("customerCategoryName", None),
            "custom_rating"                 : wc_obj.get("customerRatingName", None),
            "custom_lead_source"            : wc_obj.get("leadSourceName", None),
            "customer_details"              : remove_html_tags(wc_obj.get("description", None)),
            "_user_tags"                    : get_tags(wc_obj.get("tags", None), wc_obj.get("customerTopics", None)),
        }
    
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
    
    
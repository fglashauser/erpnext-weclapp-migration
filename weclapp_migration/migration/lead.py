import frappe
from .migration import Migration
from .contact import ContactMigration
from .address import AddressMigration
from ..tools.data import standardize_phone_number, get_salutation, get_tags

class LeadMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "lead"

    @property
    def en_doctype(self) -> str:
        return "Lead"
    
    def _get_en_obj(self, wc_obj: dict) -> dict:
        return {
            "wc_id"                 : wc_obj.get("id", None),
            "name"                  : wc_obj.get("leadNumber", None),
            "salutation"            : get_salutation(wc_obj.get("salutation", None), wc_obj.get("title", None)),
            "first_name"            : wc_obj.get("firstName", None),
            "last_name"             : wc_obj.get("lastName", None),
            "company_name"          : wc_obj.get("company", None),
            "source"                : wc_obj.get("leadSourceName", None),
            "type"                  : "Client",
            "email_id"              : wc_obj.get("email", None),
            "phone"                 : standardize_phone_number(wc_obj.get("phone", None)),
            "website"               : wc_obj.get("website", None),
            "industry"              : wc_obj.get("sectorName", None),
            "market_segment"        : wc_obj.get("customerCategoryName", None),
            "status"                : self._status(wc_obj),
            "qualification_status"  : self._qualification_status(wc_obj),
            "_user_tags"            : get_tags(wc_obj.get("tags", None), wc_obj.get("leadTopics", None)),
        }

    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        # Contacts
        contactMigration = ContactMigration(parent_doc=en_doc)
        self._migrate_linked_docs(contactMigration, en_doc, wc_obj.get("contacts", list()))
        en_doc.reload()
        primary_contact = contactMigration.get_doc_by_wc_id(wc_obj.get("primaryContactId", None))
        if primary_contact:
            email_ids   = [x.email_id for x in primary_contact.email_ids if x.is_primary]
            email_id    = email_ids[0] if email_ids else None
            phone_nos   = [x.phone for x in primary_contact.phone_nos if x.is_primary_phone]
            phone       = phone_nos[0] if phone_nos else None
            mobile_nos  = [x.phone for x in primary_contact.phone_nos if x.is_primary_mobile_no]
            mobile_no   = mobile_nos[0] if mobile_nos else None
            fax_nos     = [x.phone for x in primary_contact.phone_nos if x.custom_is_fax_number]
            fax_no      = fax_nos[0] if fax_nos else None
            en_doc.update({
                "first_name"    : primary_contact.first_name if not en_doc.first_name else en_doc.first_name,
                "last_name"     : primary_contact.last_name if not en_doc.last_name else en_doc.last_name,
                "email_id"      : email_id if not en_doc.email_id else en_doc.email_id,
                "phone"         : phone if not en_doc.phone else en_doc.phone,
                "mobile_no"     : mobile_no if not en_doc.mobile_no else en_doc.mobile_no,
                "fax"           : fax_no if not en_doc.fax else en_doc.fax,
            }).save()
            primary_contact.update({
                "is_primary_contact": True
            }).save()
        # Addresses
        addrMigration = AddressMigration(parent_doc=en_doc)
        self._migrate_linked_docs(addrMigration, en_doc, wc_obj.get("addresses", list()))
        en_doc.reload()
        primary_address = addrMigration.get_doc_by_wc_id(wc_obj.get("primaryAddressId", None))
        if primary_address:
            en_doc.update({
                "city"      : primary_address.city,
                "state"     : primary_address.state,
                "country"   : primary_address.country,
            }).save()
            primary_address.update({
                "is_primary_address": True
            }).save()

    def _status(self, wc_obj: dict) -> str:
        status = wc_obj.get("leadStatus", None)
        if status == "QUALIFIED":
            return "Lead"
        elif status == "DISQUALIFIED":
            return "Do Not Contact"
        else:
            return "Open"
        
    def _qualification_status(self, wc_obj: dict) -> str:
        status = wc_obj.get("leadStatus", None)
        if status == "QUALIFIED":
            return "Qualified"
        elif status == "DISQUALIFIED":
            return "Unqualified"
        else:
            return "In Process"
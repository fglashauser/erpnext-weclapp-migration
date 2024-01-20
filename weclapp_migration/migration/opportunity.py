import frappe
from .migration import Migration
from ..tools.data import get_date_from_weclapp_ts

class OpportunityMigration(Migration):
    @property
    def wc_doctype(self) -> str:
        return "opportunity"

    @property
    def en_doctype(self) -> str:
        return "Opportunity"

    def _get_en_obj(self, wc_obj: dict) -> dict:
        # +Bezug
        # +Kontakt
        # +Bezeichnung
        # +Verantwortlich
        # +Verkaufsphase
        # +Wahrscheinlichkeit
        # +Beschreibung
        # +Erwartetes Unterschriftsdatum
        # +Umsatz
        # +Hot Lead (Y/N)
        #
        # -Begründung
        party           = self._party(wc_obj)
        contact         = self._contact(wc_obj)
        try:
            owner       = frappe.get_doc("User", wc_obj.get("responsibleUserUsername", None))
        except frappe.exceptions.DoesNotExistError as e:
            owner       = None
        return {
            "wc_id"                 : wc_obj.get("id", None),
            "name"                  : wc_obj.get("opportunityNumber", None),        # Nummer
            "opportunity_from"      : party.doctype if party else None,             # Bezugsart
            "party_name"            : party.name if party else None,                # Bezug (Kunde / Interessent)
            "contact_person"        : contact.name if contact else None,            # Kontakt
            "custom_title"          : wc_obj.get("name", None),                     # Bezeichnung
            "custom_description"    : wc_obj.get("description", None),              # Beschreibung
            "opportunity_owner"     : owner.name if owner else None,                # Verantwortlich                       
            "sales_stage"           : wc_obj.get("salesStageName", None),           # Verkaufsphase
            "status"                : self._status(wc_obj),                         # Status / Verkaufsphase
            "probability"           : wc_obj.get("salesProbability", None),         # Wahrscheinlichkeit
            "expected_closing"      : get_date_from_weclapp_ts( \
                wc_obj.get("expectedSignatureDate", None)),                         # Erwartetes Unterschriftsdatum
            "opportunity_amount"    : wc_obj.get("revenue", None),                  # Umsatz
            "hot_lead"              : wc_obj.get("hotLead", False),                 # Hot Lead (Y/N)
            "opportunity_type"      : self.api.config.default_opportunity_type
        }
    
    def _get_tags(self, wc_obj: dict) -> list:
        pass
    
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        pass

    def _before_migration(self, wc_obj: dict) -> dict:
        return wc_obj

    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        pass

    def _party(self, wc_obj: dict) -> "frappe.Document":
        id = wc_obj.get("customerId", None)
        if not id:
            return None
        customer = next(iter(self.api.get_cache_objects("customer", lambda x: x["id"] == id)), None)
        customer = next(iter(frappe.get_all("Customer", filters={"wc_id": id})), None) if customer else None
        lead = next(iter(self.api.get_cache_objects("lead", lambda x: x["id"] == id)), None)
        lead = next(iter(frappe.get_all("Lead", filters={"wc_id": id})), None) if lead else None
        return frappe.get_doc("Customer", customer.name) if customer \
            else frappe.get_doc("Lead", lead.name) if lead \
            else None
    
    def _contact(self, wc_obj: dict) -> "frappe.Document":
        id = wc_obj.get("contactId", None)
        if not id or id == wc_obj.get("customerId", None):
            return None
        contact = next(iter(self.api.get_cache_objects("contact", lambda x: x["id"] == id)), None)
        if contact:
            contact = next(iter(frappe.get_all("Contact", filters={"wc_id": id})), None)
            if not contact:
                frappe.throw(f"Contact with WeClapp-ID {id} not found in ERPNext", frappe.DoesNotExistError)
            return frappe.get_doc("Contact", contact.name)
        else:
            return None

    def _status(self, wc_obj: dict) -> str:
        # +Verloren
        # +Erste Kontaktaufnahme
        # +Qualifikation
        # +Erstes Angebot erstellt
        # +Annahme unter Vorbehalt
        # +Auftrag erzeugt
        # +Gewonnen
        ss          = wc_obj.get("salesStageName", None)
        default     = "Open"
        map         = {
            "Open"      : ["Qualifikation"],
            "Quotation" : ["Erstes Angebot erstellt"],
            "Converted" : ["Annahme unter Vorbehalt", 
                           "Auftrag erzeugt",
                           "Gewonnen"],
            "Lost"      : ["Verloren"],
            "Replied"   : ["Erste Kontaktaufnahme"],
            "Closed"    : []
        }
        return next((k for k, v in map.items() if ss in v), default)
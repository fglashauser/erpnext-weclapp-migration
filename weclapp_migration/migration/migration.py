import frappe
from abc import ABC, abstractmethod
from ..weclapp.api import Api
from datetime import datetime

class Migration(ABC):
    """Base class for all migrations"""

    @property
    @abstractmethod
    def wc_doctype(self) -> str:
        """The WeClapp-DocType to migrate"""
        pass

    @property
    @abstractmethod
    def en_doctype(self) -> str:
        """The ERPNext-DocType to migrate to"""
        pass

    @abstractmethod
    def _get_en_obj(self, wc_obj: dict) -> dict:
        """Gets the ERPNext entity for the given WeClapp entity"""
        pass

    @abstractmethod
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        """Executes after the migration of an entity"""
        pass

    def __init__(self, api: Api = None, parent_doc: "frappe.Document" = None):
        """Initialize the migration.

        Args:
            api (Api): Established API to use for the migration
        """
        self.api = api
        self.parent_doc = parent_doc

    def clear_migrated(self):
        """Clears all migrated entities of the DocType from ERPNext"""
        query = frappe.get_all(self.en_doctype, filters={"wc_id": ["!=", None]})
        for obj in query:
            frappe.delete_doc(self.en_doctype, obj.name)

    def migrate(self, query = None, wc_obj = None) -> list["frappe.Document"]:
        """Migrates all entities of the DocType to ERPNext
        
        Args:
            query (dict, optional): Query to filter the entities. Defaults to None.
            wc_obj (dict, optional): Single entity to migrate. Defaults to None.

        Returns:
            list: List of migrated entities
        """
        objects = [wc_obj] if wc_obj else self.api.get_cache_objects(self.wc_doctype, query)
        en_docs = []
        for obj in objects:
            try:
                en_doc = self.get_doc_by_wc_id(obj["id"])
                en_doc = self._update(en_doc.name, obj) if en_doc else self._create(obj)
                self._after_migration(obj, en_doc)
                en_docs.append(en_doc)
            except Exception as e:
                self.log("Error", f"Error while migrating {self.en_doctype}", f"{e}")
        frappe.db.commit()
        return en_docs
    
    def log(self, status: str, message: str, traceback: str = None):
        """Logs a message to the log DocType."""
        doc = frappe.get_doc({
            "doctype": "Weclapp Migration Log",
            "status": status,
            "message": message,
            "traceback": traceback,
            "datetime": datetime.now()
        })
        doc.insert()
        frappe.db.commit()
    
    def get_doc_by_wc_id(self, wc_id: str) -> "frappe.Document":
        """Gets the ERPNext document by the WeClapp-ID

        Args:
            wc_id (str): WeClapp-ID of the entity

        Returns:
            frappe.Document: ERPNext document
        """
        if not wc_id:
            return None
        query = frappe.get_all(self.en_doctype, filters={"wc_id": wc_id})
        return frappe.get_doc(self.en_doctype, query[0]) if len(query) > 0 else None

    def _create(self, wc_obj: dict) -> "frappe.Document":
        """Create a new entity in ERPNext"""
        return frappe.get_doc({
            "doctype": self.en_doctype,
            **self._get_en_obj(wc_obj)
        }).insert()

    def _update(self, id, wc_obj: dict) -> "frappe.Document":
        """Update an existing entity in ERPNext"""
        return frappe.get_doc(self.en_doctype, id).update(self._get_en_obj(wc_obj)).save()
    
    def _migrate_linked_docs(self, migration: "Migration", \
                             en_doc: "frappe.Document", wc_objects: list) -> list["frappe.Document"]:
        """Migrates child-documents which are own DocTypes but should be linked.

        Args:
            migration (Migration): Migration class of child DocType
            en_doc (frappe.Document): Parent document
            wc_objects (list): List of child objects
        
        Returns:
            list: List of migrated child-documents
        """
        child_docs = []
        for wc_obj in wc_objects:
            for en_child in migration.migrate(wc_obj=wc_obj):
                en_child.append("links", {
                    "link_doctype": self.en_doctype,
                    "link_name": en_doc.name
                })
                child_docs.append(en_child.save())
        return child_docs
import frappe
from abc import ABC, abstractmethod
from ..weclapp.api import Api
from datetime import datetime
from frappe.exceptions import MandatoryError
from frappe.utils import file_manager
from pathlib import Path

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
    def _get_tags(self, wc_obj: dict) -> list:
        """Gets the tags for the given WeClapp entity"""
        pass

    @abstractmethod
    def _before_clear_migrated(self, en_doc: "frappe.Document"):
        """Executes before the clear proccess of an entity"""
        pass

    @abstractmethod
    def _before_migration(self, wc_obj: dict) -> dict:
        """Executes before the migration of an entity"""
        pass

    @abstractmethod
    def _after_migration(self, wc_obj: dict, en_doc: "frappe.Document"):
        """Executes after the migration of an entity"""
        pass

    def __init__(self, api: Api, parent_doc: "frappe.Document" = None):
        """Initialize the migration.

        Args:
            api (Api): Established API to use for the migration
        """
        self.api = api
        self.parent_doc = parent_doc

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
                en_doc = self.get_doc_by_wc_id(obj.get("id", None))
                obj = self._before_migration(obj)
                en_doc = self._update(en_doc.name, obj) if en_doc else self._create(obj)
                self._add_tags(en_doc, obj)
                self.save_attachments(obj, en_doc)
                self._after_migration(obj, en_doc)
                en_docs.append(en_doc)
            except frappe.exceptions.DuplicateEntryError as e:
                msg = f"Duplicate entry for {self.en_doctype} with WeClapp-ID {obj.get('id', None)}"
                print(msg, e, sep="\n")
                self.api.log("Error", msg, e)
            except frappe.exceptions.MandatoryError as e:
                msg = f"Mandatory field missing for {self.en_doctype} with WeClapp-ID {obj.get('id', None)}"
                print(msg, e, sep="\n")
                self.api.log("Error", msg, e)
            except frappe.exceptions.DoesNotExistError as e:
                msg = f"Parent document not found for {self.en_doctype} with WeClapp-ID {obj.get('id', None)}"
                print(msg, e, sep="\n")
                self.api.log("Error", msg, e)
            # except Exception as e:
            #     print(f"Error while migrating {self.en_doctype}")
            #     print(e)
            #     self.api.log("Error", f"Error while migrating {self.en_doctype}", f"{e}")
        frappe.db.commit()
        return en_docs
    
    def clear_migrated(self, en_doc: "frappe.Document" = None):
        """Clears all migrated entities of the DocType from ERPNext"""
        docs = [en_doc] if en_doc else frappe.get_all(self.en_doctype, filters={"wc_id": ["!=", None]})
        for doc in docs:
            #try:
            doc = frappe.get_doc(self.en_doctype, doc.name)
            self._before_clear_migrated(doc)
            frappe.delete_doc(self.en_doctype, doc.name)
            #except Exception as e:
            #    self.api.log("Error", f"Error while clearing {self.en_doctype}", f"{e}")
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
        try:
            query = frappe.get_all(self.en_doctype, filters={"wc_id": wc_id})
            return frappe.get_doc(self.en_doctype, query[0]) if len(query) > 0 else None
        except Exception as e:
            return None
    
    def save_attachments(self, wc_obj: dict, en_doc: "frappe.Document"):
        """Saves all attachments of the WeClapp entity to ERPNext

        Args:
            wc_obj (dict): WeClapp entity
            en_doc (frappe.Document): ERPNext document
        """
        files = self.api.get_cache_documents(self.wc_doctype, wc_obj["id"])
        if len(files) > 0:
            base_folder = "Home/Attachments"
            doctype_folder = f"{base_folder}/{self.en_doctype}"
            doc_folder = f"{doctype_folder}/{en_doc.name}"
            self._create_folder(base_folder, self.en_doctype)
            self._create_folder(doctype_folder, en_doc.name)
        for file in files:
            file = Path(file)
            existing_file = frappe.get_all("File", filters={"file_name": file.name,
                                                            "folder": doc_folder,
                                                            "attached_to_doctype": self.en_doctype,
                                                            "attached_to_name": en_doc.name})
            if len(existing_file) == 0:
                with open(file, "rb") as f:
                    file_doc = file_manager.save_file(file.name, f.read(),
                                           self.en_doctype, en_doc.name, doc_folder, is_private=1)
                    file_doc.update({"file_name": file.name}).save()

    def _create_folder(self, base_path: str, folder_name: str):
        """Creates a folder in the file manager.
        Checks if it exist and creates it if not.

        Args:
            base_path (str): Path of the base folder (e.g. "Home/Attachments")
            folder_name (str): Name of the folder to create
        """
        if not frappe.db.exists("File", {"file_name": folder_name, "is_folder": True, "folder": base_path}):
            folder = frappe.get_doc({
                "doctype": "File",
                "file_name": folder_name,
                "is_folder": True,
                "folder": base_path
            })
            folder.insert(ignore_permissions=True)

    def _create(self, wc_obj: dict) -> "frappe.Document":
        """Create a new entity in ERPNext"""
        return frappe.get_doc({
            "doctype": self.en_doctype,
            **self._get_en_obj(wc_obj)
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)

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
    
    def _delete_linked_childs(self, migration: "Migration", en_doc: "frappe.Document"):
        """Deletes all links of the given child-documents.

        Args:
            migration (Migration): Migration class of child DocType
            en_doc (frappe.Document): Parent document
        """
        links = frappe.get_all("Dynamic Link", filters={"link_doctype": self.en_doctype, "link_name": en_doc.name, "parenttype": migration.en_doctype})
        for link in links:
            link = frappe.get_doc("Dynamic Link", link.name)
            child = frappe.get_doc(migration.en_doctype, link.parent)
            link.delete()
            frappe.db.commit()
            migration.clear_migrated(child)

    def _add_tags(self, en_doc: "frappe.Document", wc_obj: dict):
        """Adds tags to the given document

        Args:
            en_doc (frappe.Document): Document to add tags to
            wc_obj (dict): WeClapp entity
        """
        wc_tags = self._get_tags(wc_obj)
        if not wc_tags:
            return
        wc_tags = [tag["name"] for tag in wc_tags]
        en_tags = en_doc.get_tags()
        new_tags = [tag for tag in wc_tags if tag not in en_tags]
        for tag in new_tags:
            en_doc.add_tag(tag)
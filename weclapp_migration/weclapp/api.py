import frappe
import requests
from pysondb import PysonDB
from pathlib import Path
import shutil
from datetime import datetime

class Api:
    """Class for accessing WeClapp API and caching data locally."""
    def __init__(self):
        self.config = frappe.get_single("Weclapp Migration Settings")

    def __enter__(self):
        self.session = requests.Session()
        self.session.headers = {
            "Content-Type"          : "application/json",
            "AuthenticationToken"   : self.config.get_password("wc_api_token")
        }
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
    
    def setup_cache(self):
        """Clears the cache & log and creates the cache folders."""
        cache_base = Path(self._get_cache_base())
        # Clear cache
        if cache_base.exists():
            shutil.rmtree(cache_base)
        # Clear log
        frappe.db.sql("DELETE FROM `tabWeclapp Migration Log`")
        frappe.db.commit()
        # Create cache folders
        Path(cache_base.joinpath("documents")).mkdir(parents=True, exist_ok=True)

    def cache_doctype(self, doctype: str):
        """Caches all entities of the given DocType and saves them in JSON-files.
        Overrides existing files."""
        # Fetch entities and save them in JSON-files
        wc_data = self._get_all(doctype)
        cache_db = PysonDB(f"{self._get_cache_base()}{doctype}.json")
        cache_db.add_many(wc_data)
        for obj in wc_data:
            # Fetch documents and save them in files
            documents = self._request(f"document", "GET",
                                      params={
                                          "entityName": doctype,
                                          "entityId": obj["id"]
                                      }).json()["result"]
            for doc in documents:
                # Add meta data to document-object: doctype and id
                doc["entityName"] = doctype
                doc["entityId"] = obj["id"]
                base_path = Path(self._get_cache_base()).joinpath(f"documents/{doctype}/{obj['id']}/")
                base_path.mkdir(parents=True, exist_ok=True)
                with open(base_path.joinpath(doc["name"]), "wb") as file:
                    file.write(self._request(f"document/id/{doc['id']}/download", "GET").content)
            
            if doctype in self.config.wc_mail_doctypes:
                # Fetch archived emails and save them in JSON-files
                emails = self._request(f"archivedEmail", "GET",
                                       params={
                                           "entityName": doctype,
                                           "entityId": obj["id"],
                                           "serializeNulls": "true"
                                       }).json()["result"]
                for email in emails:
                    # Add meta data to email-object: doctype and id
                    email["entityName"] = doctype
                    email["entityId"] = obj["id"]
                cache_db = PysonDB(f"{self._get_cache_base()}archivedEmail.json")
                cache_db.add_many(emails)

    def get_cache_objects(self, doctype: str, query = None):
        """Gets all cached entities of the given DocType."""
        cache_db = PysonDB(f"{self._get_cache_base()}{doctype}.json")
        return cache_db.get_by_query(query).values() if query else cache_db.get_all().values()
    
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

    def _get_cache_base(self) -> str:
        return f"{frappe.local.site}/private/weclapp_migration/cache/"

    def _get_all(self, doctype: str):
        """Gets all entities of the given DocType."""
        pages = (self._get_count(doctype) + self.config.wc_page_size - 1) // self.config.wc_page_size
        result = []
        for page in range(1, pages + 1):
            result += self._get_page(doctype, page)
        return result

    def _get_count(self, doctype: str) -> int:
        """Gets the amount of entities of the given DocType."""
        return int(self._request(f"{doctype}/count", "GET").json()["result"])

    def _get_page(self, doctype: str, page: int):
        """Gets a page of entities of the given DocType."""
        return self._request(doctype, "GET",
                             params={
                                 "serializeNulls": "true",
                                 "pageSize": self.config.wc_page_size,
                                 "page": page
                            }) \
                            .json()["result"]

    def _request(self, doctype : str, method: str, data: dict = None, params: dict = None):
        """Makes a request to WeClapp API."""
        url = f"{self.config.wc_api_base}{doctype}"
        try:
            response = self.session.request(method=method, url=url, json=data, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            frappe.throw(f"WeClapp API-Error: {response.text}")

        return response

    
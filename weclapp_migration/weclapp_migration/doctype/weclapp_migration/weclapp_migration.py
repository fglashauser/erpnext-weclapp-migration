# Copyright (c) 2023, PC-Giga (Florian Glashauser) and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document
from ....weclapp.api import Api
from ....migration.customer import CustomerMigration
from ....migration.industry_type import IndustryTypeMigration
from ....migration.market_segment import MarketSegmentMigration
from ....migration.lead_source import LeadSourceMigration
from ....migration.lead import LeadMigration
from ....migration.salutation import SalutationMigration
from ....migration.uom import UomMigration
from ....migration.item import ItemMigration
from ....migration.user import UserMigration
from ....migration.sales_stage import SalesStageMigration
from ....migration.opportunity import OpportunityMigration

class WeclappMigration(Document):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = frappe.get_single("Weclapp Migration Settings")

	@frappe.whitelist()
	def cache_weclapp_data(self):
		"""Caches all data from WeClapp to local cache-database (JSON-files).
		"""
		frappe.enqueue_doc(
			"Weclapp Migration",
			self.name,
			"cache_weclapp_data_job",
			queue="long",
			timeout=5000
		)
		#self.cache_weclapp_data_job()

	def cache_weclapp_data_job(self):
		with Api() as api:
			api.setup_cache()
			for doctype in self.config.wc_doctypes:
				try:
					api.cache_doctype(doctype)
					api.log("Success", f"Successfully cached: {doctype}")
				except Exception as e:
					api.log("Error", f"Error while caching {doctype}", f"{e}")

	@frappe.whitelist()
	def migrate_weclapp_data(self):
		"""Migrates selected data from Cache to ERPNext."""
		frappe.enqueue_doc(
			"Weclapp Migration",
			self.name,
			"migrate_weclapp_data_job",
			queue="long",
			timeout=5000
		)
		#self.migrate_weclapp_data_job()

	def migrate_weclapp_data_job(self):
		with Api() as api:
			industryTypeMig = IndustryTypeMigration(api)
			marketSegmentMig = MarketSegmentMigration(api)
			leadSourceMig = LeadSourceMigration(api)
			customerMigration = CustomerMigration(api)
			leadMigration = LeadMigration(api)
			salutationMigration = SalutationMigration(api)
			uomMig = UomMigration(api)
			itemMig = ItemMigration(api)
			userMig = UserMigration(api)
			opportunityMig = OpportunityMigration(api)
			salesStageMig = SalesStageMigration(api)


			salesStageMig.migrate()
			userMig.migrate()
			uomMig.migrate()
			salutationMigration.migrate()
			industryTypeMig.migrate()
			marketSegmentMig.migrate()
			leadSourceMig.migrate()
			itemMig.migrate()
			leadMigration.migrate()
			customerMigration.migrate()
			opportunityMig.migrate()


			#customerMigration.migrate()
			#leadMigration.migrate()
			# test_doc = frappe.get_doc({	"doctype": "Customer", "name": "14104"})
			# test_doc.load_from_db()
			# print(test_doc)
			#leadMigration.migrate(query=lambda x: x["leadNumber"] == "23073")
			#customerMigration.migrate(lambda x: x["customerNumber"] == "13977")
			#opportunityMig.migrate(lambda x: x["opportunityNumber"] == "1001")

	@frappe.whitelist()
	def clear_migrated_data(self):
		"""Clears all migrated data from ERPNext."""
		with Api() as api:
			# Test: Customers
			customerMigration = CustomerMigration(api)
			leadMigration = LeadMigration(api)
			customerMigration.clear_migrated(frappe.get_doc("Customer", "13985"))
			#leadMigration.clear_migrated()

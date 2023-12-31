# Copyright (c) 2023, PC-Giga (Florian Glashauser) and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class WeclappMigrationSettings(Document):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.wc_page_size 		= 100
		self.wc_doctypes		= [
			"accountingTransaction",
			"article",
			"articleAccountingCode",
			"articleCategory",
			"articleItemGroup",
			"articlePrice",
			"articleRating",
			"articleStatus",
			"articleSupplySource",
			"attendance",
			"bankAccount",
			"batchNumber",
			"blanketPurchaseOrder",
			"calendar",
			"calendarEvent",
			"campaign",
			"campaignParticipant",
			"cashAccount",
			"commercialLanguage",
			"companySize",
			"contact",
			"contract",
			"contractAuthorizationUnit",
			"contractBillingGroup",
			"contractTerminationReason",
			"costCenter",
			"costCenterGroup",
			"costType",
			"crmCallCategory",
			"crmEvent",
			"crmEventCategory",
			"currency",
			"customAttributeDefinition",
			"customer",
			"customerCategory",
			"customerLeadLossReason",
			"customerTopic",
			"customsTariffNumber",
			"externalConnection",
			"financialYear",
			"fulfillmentProvider",
			"incomingGoods",
			"internalTransportReference",
			"lead",
			"leadRating",
			"leadSource",
			"ledgerAccount",
			"legalForm",
			"loadingEquipmentIdentifier",
			"manufacturer",
			"notification",
			"opportunity",
			"opportunityTopic",
			"opportunityWinLossReason",
			"party",
			"partyRating",
			"paymentMethod",
			"paymentRun",
			"paymentRunItem",
			"personDepartment",
			"personRole",
			"personalAccountingCode",
			"pick",
			"pickCheckReason",
			"placeOfService",
			"productionOrder",
			"productionWorkSchedule",
			"productionWorkScheduleAssignment",
			"purchaseInvoice",
			"purchaseOpenItem",
			"purchaseOrder",
			"purchaseOrderRequest",
			"quotation",
			"remotePrintJob",
			"salesInvoice",
			"salesOpenItem",
			"salesOrder",
			"salesStage",
			"sector",
			"sepaDirectDebitMandate",
			"serialNumber",
			"shelf",
			"shipment",
			"shipmentMethod",
			"shipmentReturnAssessment",
			"shipmentReturnError",
			"shipmentReturnReason",
			"shipmentReturnRectification",
			"shippingCarrier",
			"storageLocation",
			"storagePlace",
			"storagePlaceBlockingReason",
			"storagePlaceSize",
			"supplier",
			"tag",
			"tax",
			"taxDeterminationRule",
			"termOfPayment",
			"ticket",
			"ticketAssignmentRule",
			"ticketCategory",
			"ticketChannel",
			"ticketFaq",
			"ticketServiceLevelAgreement",
			"ticketStatus",
			"ticketType",
			"title",
			"translation",
			"transportationOrder",
			"unit",
			"user",
			"variantArticle",
			"variantArticleAttribute",
			"variantArticleVariant",
			"warehouse",
			"warehouseStock",
			"warehouseStockMovement",
			"webhook",
			"weclappOs"
		]
		self.wc_mail_doctypes	= [
			"salesInvoice",
			"salesOrder",
			"quotation",
			"ticket"
		]

# Copyright 2018 ACSONE SA/NV (https://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Account invoice tax note",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "development_status": "Production/Stable",
    "summary": "Print tax notes on customer invoices",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Localization / Accounting",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": ["reports/report_invoice_document.xml", "views/account_tax_views.xml"],
    "installable": True,
}

# Copyright 2018 Domatix S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    invoiceplane_id = fields.Integer(
        string='InvoicePlane id')

    invoiceplane_import = fields.Boolean(
        string='InvoicePlane Import')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    invoiceplane_id = fields.Integer(
        string='InvoicePlane id')

    invoiceplane_import = fields.Boolean(
        string='InvoicePlane Import')

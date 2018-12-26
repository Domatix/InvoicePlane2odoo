# Copyright 2018 Domatix S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoiceplane_id = fields.Integer(
        string='InvoicePlane id')

    invoiceplane_import = fields.Boolean(
        string='InvoicePlane Import')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    invoiceplane_id = fields.Integer(
        string='InvoicePlane id')

    invoiceplane_import = fields.Boolean(
        string='InvoicePlane Import')

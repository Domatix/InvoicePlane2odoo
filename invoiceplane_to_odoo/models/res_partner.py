# Copyright 2018 Domatix S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoiceplane_id = fields.Integer(
        string='InvoicePlane id')

    invoiceplane_import = fields.Boolean(
        string='InvoicePlane Import')

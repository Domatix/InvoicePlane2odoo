# Copyright 2018 Domatix S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from datetime import datetime


class InvoiceplaneTracking(models.Model):
    _name = "invoiceplane.tracking"
    _description = "Displays imported data"
    _order = "date desc"

    name = fields.Char(
        string='Name')

    date = fields.Datetime(
        string='Date')

    partner_count = fields.Integer(
        string='Partner Count',
        compute='_compute_partner_count',
        store=True)
    order_count = fields.Integer(
        string='Partner Count',
        compute='_compute_sale_order_count',
        store=True)
    invoice_count = fields.Integer(
        string='Partner Count',
        compute='_compute_invoice_count',
        store=True)
    partner_lines = fields.One2many(
        comodel_name='invoiceplane.tracking.line',
        inverse_name='import_client_line',
        string='Partner Lines')
    order_lines = fields.One2many(
        comodel_name='invoiceplane.tracking.line',
        inverse_name='import_order_line',
        string='Order Lines')
    invoice_lines = fields.One2many(
        comodel_name='invoiceplane.tracking.line',
        inverse_name='import_invoice_line',
        string='Invoice Lines')

    @api.depends('partner_lines')
    def _compute_partner_count(self):
        self.partner_count = len(self.partner_lines.mapped('partner_id').ids)

    @api.depends('order_lines')
    def _compute_sale_order_count(self):
        self.order_count = len(self.order_lines.mapped('order_id').ids)

    @api.depends('invoice_lines')
    def _compute_invoice_count(self):
        self.invoice_count = len(self.invoice_lines.mapped('invoice_id').ids)

    @api.multi
    def list_of_partners(self):
        action = {
            'domain': "[('id', 'in', " + str(
                                            self.partner_lines.mapped(
                                                    'partner_id').ids) + " )]",
            'name': 'Imported Partners',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
                  }
        return action

    @api.multi
    def list_of_sales_orders(self):
        action = {
            'domain': "[('id', 'in', " + str(
                                            self.order_lines.mapped(
                                                    'order_id').ids) + " )]",
            'name': 'Imported Partners',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
                  }
        return action

    @api.multi
    def list_of_invoices(self):
        action = {
            'domain': "[('id', 'in', " + str(
                                            self.invoice_lines.mapped(
                                                    'invoice_id').ids) + " )]",
            'name': 'Imported Partners',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
                  }
        return action


class InvoiceplaneTrackingLine(models.Model):
    _name = "invoiceplane.tracking.line"

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order')

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice')

    import_client_line = fields.Many2one(
        comodel_name='invoiceplane.tracking',
        string='Partner')

    import_order_line = fields.Many2one(
        comodel_name='invoiceplane.tracking',
        string='Sale Order')

    import_invoice_line = fields.Many2one(
        comodel_name='invoiceplane.tracking',
        string='Invoice')

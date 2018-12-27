# Copyright 2018 Domatix S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
import base64
import tempfile
import json
import vatnumber
from datetime import datetime


class ImportData(models.TransientModel):
    _name = "invoiceplane.import.data"
    _description = "Import data through file"

    # Partners
    partner_filename = fields.Char(
        string='Filename')
    partner_file = fields.Binary(
        string='ip_clients',
        help="Import partners from json.")

    # Sale Orders
    sale_order_filename = fields.Char(
        string='Filename')
    sale_order_file = fields.Binary(
        string='ip_quotes',
        help="Import Sale Order from this table.")

    # Sale Order Lines
    sale_order_line_filename = fields.Char(
        string='Filename')
    sale_order_line_file = fields.Binary(
        string='ip_quotes_items',
        help="Import Sale Order Lines from this table.")

    # Invoices
    invoice_filename = fields.Char(
        string='Filename')
    invoice_file = fields.Binary(
        string='ip_invoices',
        help="Import Sale Order from this table.")

    # Invoice Lines
    invoice_line_filename = fields.Char(
        string='Filename')
    invoice_line_file = fields.Binary(
        string='ip_invoice_items',
        help="Import Sale Order Lines from this table.")

    def import_partner(self, partner_data):
        partner_obj = self.env['res.partner']
        state_obj = self.env['res.country.state']
        country_obj = self.env['res.country']
        partner_array = []
        for partner in partner_data:
            partner_id = partner_obj.search([
                ('invoiceplane_id', '=', partner['client_id'])])

            if not partner_id:
                partner_id = partner_obj.search([
                    ('name', '=', partner['client_name']),
                    ('customer', '=', True)])
                if partner_id:
                    partner_id = partner_id[0]
                    partner_id.write({'invoiceplane_id': partner['client_id']})

            country_id = country_obj.search([
                ('code', '=', partner['client_country'])
            ])
            if not country_id:
                country_id = country_obj.search([
                    ('code', '=', 'ES')
                ])
            state_id = state_obj.search([
                ('name', '=', partner['client_state']),
                ('country_id', '=', country_id.id)
            ])
            if not partner_id:
                values = {
                    'invoiceplane_id': partner['client_id'],
                    'name': partner['client_name'],
                    'mobile': partner['client_mobile'],
                    'phone': partner['client_phone'],
                    'email': partner['client_email'],
                    'street': partner['client_address_1'],
                    'city': partner['client_city'],
                    'state_id': state_id[0].id if state_id else False,
                    'zip': partner['client_zip'],
                    'country_id': country_id.id if country_id else False,
                    'customer': True,
                    'supplier': False,
                    'opt_out': True,
                    'vat': partner['client_vat_id']
                    if vatnumber.check_vat(partner['client_vat_id'])
                    else False,
                    'type': 'invoice',
                    'invoiceplane_import': True,
                }

                partner_id = partner_obj.create(values)
                partner_array.append(partner_id.id)
        return partner_array

    def import_sale_order(self, sale_order_data):
        sale_obj = self.env['sale.order']
        res_obj = self.env['res.partner']
        order_array = []
        for order in sale_order_data:
            order_id = sale_obj.search([
                ('invoiceplane_id', '=', order['quote_id'])])

            if not order_id:
                partner_id = res_obj.search([
                    ('invoiceplane_id', '=', order['client_id'])])

                values = {
                    'invoiceplane_id': order['quote_id'],
                    'partner_id': partner_id[0].id,
                    'user_id': self.env.user.id,
                    'date_order': order['quote_date_created'],
                    'validity_date': order['quote_date_expires'],
                    'client_order_ref': order['quote_number'],
                    'invoiceplane_import': True,
                }

                sale_id = sale_obj.create(values)
                order_array.append(sale_id.id)
        return order_array

    def import_sale_order_line(self, sale_order_line_data):
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']
        for order_line in sale_order_line_data:
            order_id = sale_obj.search(
                [('invoiceplane_id', '=', order_line['quote_id'])])

            order_line_id = sale_line_obj.search(
                [('invoiceplane_id', '=', order_line['item_id'])])

            product_id = product_obj.search([
                ('name', '=', order_line['item_name'])])
            if not product_id:
                product_id = product_obj.create(
                    {'name': order_line['item_name'],
                     'description': order_line['item_description']})
            if not order_line_id:
                values = {
                    'invoiceplane_id': order_line['item_id'],
                    'order_id': order_id.id,
                    'name': order_line['item_description'],
                    'product_id': product_id[0].id,
                    'product_uom_qty': order_line['item_quantity'],
                    'price_unit': order_line['item_price'],
                    'invoiceplane_import': True,
                }

                sale_line_obj.create(values)

    def import_invoice(self, invoice_data):
        invoice_obj = self.env['account.invoice']
        res_obj = self.env['res.partner']
        invoice_array = []
        for invoice in invoice_data:
            invoice_id = invoice_obj.search(
                [('invoiceplane_id', '=', invoice['invoice_id'])])

            if not invoice_id:
                partner_id = res_obj.search([
                    ('invoiceplane_id', '=', invoice['client_id'])])
                values = {
                    'number': invoice['invoice_number'],
                    'invoiceplane_id': invoice['invoice_id'],
                    'partner_id': partner_id[0].id,
                    'name': invoice['invoice_number'],
                    'user_id': self.env.user.id,
                    'date_invoice': invoice['invoice_date_created'],
                    'date_due': invoice['invoice_date_due'],
                    'invoiceplane_import': True,
                }

                invoice_id = invoice_obj.create(values)
                invoice_array.append(invoice_id.id)
        return invoice_array

    def import_invoice_line(self, invoice_line_data):
        invoice_line_obj = self.env['account.invoice.line']
        invoice_obj = self.env['account.invoice']
        product_obj = self.env['product.product']
        tax_obj = self.env['account.tax']
        tax_id = tax_obj.browse([1])
        for invoice_line in invoice_line_data:
            invoice_id = invoice_obj.search(
                [('invoiceplane_id', '=', invoice_line['invoice_id'])])

            invoice_line_id = invoice_line_obj.search(
                [('invoiceplane_id', '=', invoice_line['item_id'])])

            product_id = product_obj.search([
                ('name', '=', invoice_line['item_name'])])
            if not product_id:
                product_id = product_obj.create({
                    'name': invoice_line['item_name'],
                    'description': invoice_line['item_description']})
            if not invoice_line_id:

                values = {
                    'invoiceplane_id': invoice_line['item_id'],
                    'invoice_id': invoice_id.id,
                    'name': invoice_line['item_description'],
                    'product_id': product_id[0].id,
                    'quantity': invoice_line['item_quantity'],
                    'price_unit': invoice_line['item_price'],
                    'account_id': product_id[0].categ_id.
                    property_account_income_categ_id.id,
                    'invoice_line_tax_ids': [(4, product_id[0].taxes_id.id)]
                    if product_id[0].taxes_id else [(4, tax_id.id)],
                    'invoiceplane_import': True,
                }

                invoice_line_id = invoice_line_obj.create(values)

    @api.multi
    def action_import(self):
        import_obj = self.env['invoiceplane.tracking']
        import_id = import_obj.create(
            {'name': 'Import ' + ' - ' + datetime.now().strftime('%d-%m-%Y'),
             'date': datetime.now(), })
        # Partners
        if self.partner_file:
            f = tempfile.NamedTemporaryFile()
            f.write(base64.decodestring(self.partner_file))
            f.flush()
            with open(f.name, 'r') as handle:
                fixed_json = ''.join(line for line in handle
                                     if not line.startswith('//'))
                partner_data = json.loads(fixed_json)
            f.close()
            partner_ids = self.import_partner(partner_data)
            for partner_id in partner_ids:
                import_id.write({'partner_lines': [(0, 0,
                                                    {'partner_id': partner_id})
                                                   ]})

        # Sale Orders
        if self.sale_order_file:
            f = tempfile.NamedTemporaryFile()
            f.write(base64.decodestring(self.sale_order_file))
            f.flush()
            with open(f.name, 'r') as handle:
                fixed_json = ''.join(line for line in handle
                                     if not line.startswith('//'))
                sale_order_data = json.loads(fixed_json)
            f.close()
            order_ids = self.import_sale_order(sale_order_data)
            for order_id in order_ids:
                import_id.write({'order_lines': [(0, 0,
                                                  {'order_id': order_id})]})

        # Sale Order Lines
        if self.sale_order_line_file:
            f = tempfile.NamedTemporaryFile()
            f.write(base64.decodestring(self.sale_order_line_file))
            f.flush()
            with open(f.name, 'r') as handle:
                fixed_json = ''.join(line for line in handle
                                     if not line.startswith('//'))
                sale_order_line_data = json.loads(fixed_json)

            f.close()
            self.import_sale_order_line(sale_order_line_data)

        # Invoices
        if self.invoice_file:
            f = tempfile.NamedTemporaryFile()
            f.write(base64.decodestring(self.invoice_file))
            f.flush()
            with open(f.name, 'r') as handle:
                fixed_json = ''.join(line for line in handle
                                     if not line.startswith('//'))
                invoice_data = json.loads(fixed_json)
            f.close()
            invoice_ids = self.import_invoice(invoice_data)
            for invoice_id in invoice_ids:
                import_id.write({'invoice_lines': [(0, 0,
                                                    {'invoice_id': invoice_id})
                                                   ]})

        # Invoice Lines
        if self.invoice_line_file:
            f = tempfile.NamedTemporaryFile()
            f.write(base64.decodestring(self.invoice_line_file))
            f.flush()
            with open(f.name, 'r') as handle:
                fixed_json = ''.join(line for line in handle
                                     if not line.startswith('//'))
                invoice_line_data = json.loads(fixed_json)
            f.close()
            self.import_invoice_line(invoice_line_data)

        # Confirm Invoices
        if self.invoice_line_file:
            invoices = self.env['account.invoice'].browse(invoice_ids)
            for invoice in invoices:
                if invoice.invoice_line_ids:
                    try:
                        invoice.compute_taxes()
                        invoice.action_invoice_open()
                    except ValueError:
                        continue
                    invoice.number = invoice.name

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'invoiceplane.tracking',
            'target': 'current',
            'res_id': import_id.id,
            'type': 'ir.actions.act_window'
        }

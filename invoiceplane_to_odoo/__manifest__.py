# Copyright 2017-2018 Domatix S.L
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'InvoicePlane To Odoo',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'author': 'Domatix',
    'version': '11.0.1.0.0',
    'website': 'https://github.com/Domatix',
    'summary': "Migrates data from InvoicePlane to Odoo",
    'depends': [
        'sale_management',
    ],
    'data': [
        'wizard/import_data.xml',
        'views/invoiceplane_tracking.xml',
    ],

}

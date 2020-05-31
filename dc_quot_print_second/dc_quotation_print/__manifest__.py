# -*- coding: utf-8 -*-
{
    'name': 'DC Quotations second',
    'version': '1.0',
    'category': 'Operations/Inventory/Delivery',
    'description': """""",
    'depends': ['base_setup','sale', 'cost_sheet_quotations'],
    'data': [
        'report/quotation-simple.xml',
        'report/quotation-details.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
        ],
    'demo': [],
    'installable': True,
    'application': True,
}

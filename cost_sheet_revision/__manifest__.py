# -*- coding: utf-8 -*-

{
    'name': 'Cost Sheet rev',
    'version': '1.0',
    'depends': ['mail','base','crm','mrp','project','product','sale','product','cost_sheet_quotations'],
    'category': 'sale','crm'
    'summary': 'Handle lunch orders of your employees',
    'description': """
The base module to manage lunch.
================================
Cost sheet from CRM, Generate Quotation
    """,
    'data': [
         # 'views/sale.xml',
        'views/view.xml'
        ,
        'data/sequence.xml',
    ],
    'installable': True,
    'application': True,
}

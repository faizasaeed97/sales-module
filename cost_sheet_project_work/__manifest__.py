# -*- coding: utf-8 -*-

{
    'name': 'Cost Sheet Project',
    'sequence': 1222,
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
        'security/ir.model.access.csv',
        'views/project.xml'


    ],
    'installable': True,
    'application': True,
}

# -*- coding: utf-8 -*-

{
    'name': 'Cost Sheet',
    'sequence': 1222,
    'version': '1.0',
    'depends': ['mail', 'base', 'crm', 'mrp', 'project', 'product', 'sale', 'product','account','design_creative_custom'],
    'category': 'sale', 'crm'
                        'summary': 'Handle lunch orders of your employees',
    'description': """
The base module to manage lunch.
================================
Cost sheet from CRM, Generate Quotation
    """,
    'data': [
        'security/ir.model.access.csv',
        'security/recrules.xml',
        'views/sale.xml',
        # 'wizard/wizard_view.xml',
        'views/view.xml',
        'data/demo.xml',
        'data/sequence.xml',
        'data/sequence_additional_cost_sheet.xml',
        'reports/repair_order_print.xml',
        'reports/report.xml',
        'reports/quotation_print.xml',
    ],
    'installable': True,
    'application': True,
}

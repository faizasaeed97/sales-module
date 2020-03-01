# coding: utf-8


{
    'name': 'Import hr contract',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales,Purchase',
    'summary': "Import a purchase & a sale order from an .xls/.xlsx file",
    'depends': ['base',
                'web'
                ],
    'data': [
        'wizard/import_purchase_order.xml',
    ],

    'installable': True,
    'application': True,

}

{
    'name': 'Invoice report custom',
    'description': 'Apply discount On Invoice Total And Sales Orders',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'category': 'discount',
    'author': 'kashif',
    'website': '',
    'depends': [
'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        # 'views/journal_entries_report.xml'
    ],
    'application': True,
    'installable': True,
}



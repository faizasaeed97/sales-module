{
    'name': 'design creative custom',
    'description': 'design creative customization',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'category': 'custom',
    'author': 'kashif',
    'website': '',
    'depends': [
        'base',
        'hr',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_emplouee_custom.xml',
        'views/hr_contract_custom.xml',
    ],
    'installable': True,
}


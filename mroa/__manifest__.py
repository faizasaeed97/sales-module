{
    'name': 'MROA Implementation',
    'version': '1.0',
    'category': 'Fleet/Manufacturing',
    'description': """
Modifications Required For MROA
===============================
    """,
    'author': 'Ahmed Khakwani',
    'depends': ['fleet', 'maintenance', 'repair', 'base', 'stock', 'mrp'],
    'data': [
        'fleet/fleet_view.xml',
        'product/product.xml',
        'product/reference_price_view.xml',
        'fleet/engines_view.xml',
        'fleet/apu_view.xml',
        'fleet/configuration_mng.xml',
        'process_sheet/process_sheet.xml',
        'views/system_menu.xml',
        'views/sequence.xml',
        'views/mrp_view.xml',
        'security/ir.model.access.csv',
        'security/mroa_security.xml'
    ],
    'installable': True,
    'application': True,
}

# -*- coding : utf-8 -*-

{
    'name'          : 'Stock Transfer Backdate and Remarks in Odoo',
    'version'       : '13.0.0.1',
    'category'      : 'Warehouse',
    'summary'       : 'Custom back date will be transfer to stock entries and accounting entries',
    'author'        : 'Junaid',
    'depends'       : ['base','sale_management','stock','stock_account'],
    'data'          : [
                        'wizard/stock_wizards_views.xml',
                        'views/stockpicking_views.xml',
                        'views/stock_move_views.xml',
                        ],
    'installable'   : True,
    'auto_install'  : False,
    "images":["static/description/Banner.png"],
}

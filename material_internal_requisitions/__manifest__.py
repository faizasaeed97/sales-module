{
    'name': 'Product/Material Internal Requisitions by Employees/Users',
    'version': '12.0.1',
    'summary': """This module allow your employees/users to create Internal Requisitions.""",
    'author': 'Gerrys Apps',
    'website': 'http://www.gerrys.net',
    'category': 'Warehouse',
    'depends': ['stock','product','hr','purchase_requisition_stock',],
    'data':[
        'security/ir.model.access.csv',
        'security/requisition_security.xml',
        'data/requisition_sequence.xml',
        'data/employee_approval_template.xml',
        'data/confirm_template.xml',
        'report/requisition_report.xml',
        'views/requisition_view.xml',
        'views/hr_employee_view.xml',
        'views/stock_picking_view.xml',
        'views/automatic_purchase_request.xml',
    ],
    'installable' : True,
    'application' : False,
}
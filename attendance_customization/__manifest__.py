# -*- coding: utf-8 -*-

{
    'name': 'Attendance Customization',
    'sequence': 1222,
    'version': '1.0',
    'depends': ['mail', 'base', 'hr_payroll', 'crm', 'mrp', 'project', 'product', 'sale', 'product', 'hr'],
    'category': 'sale', 'crm'
                        'summary': 'Handle lunch orders of your employees',
    'description': """
The base module to manage lunch.
================================
Cost sheet from CRM, Generate Quotation
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
        'views/leave.xml',
        'views/hr_emp.xml',
        'views/import_data.xml',
        'views/hr_emp_define.xml',

        # 'wizard/attend_summery_wiz.xml',
        # 'report/emp_cost_report.xml',
        'report/attendance_summery.xml',
        'wizard/attend_summery_wiz.xml',
        'report/empcsotxls.xml',

        # 'report/weekly_attendance_report.xml',

    ],
    'installable': True,
    'application': True,
}

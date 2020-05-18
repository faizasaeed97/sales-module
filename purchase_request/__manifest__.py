{
    "name": "Purchase Request",
    "version": "13.0.1",
    "summary": "Use this module to have notification of requirements of "
               "materials and/or external services and keep track of such "
               "requirements.",
    "category": "Purchase Management",
    "depends": [
        "purchase",
        "product"
    ],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "views/purchase_request_view.xml",
        "reports/report_purchaserequests.xml",
        "views/purchase_request_report.xml",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",

    ],
    
    'installable': True,
    'application':True,

}
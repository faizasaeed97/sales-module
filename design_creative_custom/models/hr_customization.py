from odoo import models, fields, api


class inherithremploye(models.Model):
    _inherit = 'hr.employee'

    bahrain_expact=fields.Selection([('Bahraini', 'Bahraini'),('Expats', 'Expats')], string='Bahranis/Expacts',)

    muslim = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Muslim', )

    age=fields.Char(string="Age")
    dependent = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Dependent', )

    cpr_no = fields.Char(string="CPR NO")

    cpr_exp_date = fields.Date(string="CPR Expiry")

    passport_exp_date = fields.Date(string="Passport Expiry")

    rp_exp_date = fields.Date(string="RP Expiry")

    veh_alloted = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Vehicle Alloted', )

    accomodation = fields.Selection([('YES', 'YES'), ('NO', 'NO')], string='Acomodation', )


class inheritcontract(models.Model):
    _inherit = 'hr.contract'






    
    housing_allowance=fields.Float("Housing Allowance",default=0.00)
    travel_allowance=fields.Float("Travel Allowance",default=0.00)
    increment_Date = fields.Date(string="Increment Date")
    increment_Amount=fields.Float("Increment Amount",default=0.00)
    leave_Status = fields.Selection([('Active', 'Active'), ('Terminated', 'Terminated'), ('Resigned', 'Resigned'),('Vacation', 'Vacation')], string='Leave Status', )
    leave_due=fields.Float("Leave Due",default=0.00)
    leave_amount=fields.Float("Leave Amount",default=0.00)
    total_work_experience= fields.Char(string="Total Work Experience")
    indemnity= fields.Char(string="Indemnity")
    tenure= fields.Char(string="Tenure")
    sponsorship= fields.Selection([('Design Creative', 'Design Creative'), ('Design Grafix', 'Design Grafix')], string='Sponsorship', )
    work_location = fields.Selection([('DG', 'DG'), ('DC', 'DC')], string='Work Location', )



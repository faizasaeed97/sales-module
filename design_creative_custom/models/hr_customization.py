from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError



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
    designation=fields.Many2one('employee.designation',)



class inheritcontracts(models.Model):
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
    gosi_Salary_Deduction=fields.Float("GOSI Salery deduction",default=0.00)
    hourly_salery=fields.Float("Hourly salery",default=0.00)
    Misce_Allowance=fields.Float("Miscellaneous Allowance",default=0.00)
    OT=fields.Float("OT",default=0.00)
    OT1 = fields.Float("OT 1", default=0.00)
    OT2 = fields.Float("OT 2", default=0.00)
    OTw = fields.Float("OT(W)", default=0.00)

class accacc_mov(models.Model):
    _inherit = 'account.account'

    def _set_opening_debit_credit(self, amount, field):
        """ Generic function called by both opening_debit and opening_credit's
        inverse function. 'Amount' parameter is the value to be set, and field
        either 'debit' or 'credit', depending on which one of these two fields
        got assigned.
        """
        opening_move = self.company_id.account_opening_move_id

        if not opening_move:
            raise UserError(_("You must first define an opening move."))

        if opening_move.state == 'draft':
            # check whether we should create a new move line or modify an existing one
            opening_move_line = self.env['account.move.line'].search([('account_id', '=', self.id),
                                                                      ('move_id','=', opening_move.id),
                                                                      (field,'!=', False),
                                                                      (field,'!=', 0.0)]) # 0.0 condition important for import

            counter_part_map = {'debit': opening_move_line.credit, 'credit': opening_move_line.debit}
            # No typo here! We want the credit value when treating debit and debit value when treating credit

            if opening_move_line:
                if amount:
                    # modify the line
                    opening_move_line.with_context(check_move_validity=False)[field] = amount
                elif counter_part_map[field]:
                    # delete the line (no need to keep a line with value = 0)
                    opening_move_line.with_context(check_move_validity=False).unlink()
            elif amount:
                # create a new line, as none existed before
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': _('Opening balance'),
                        field: amount,
                        'move_id': opening_move.id,
                        'account_id': self.id,
                })

            # Then, we automatically balance the opening move, to make sure it stays valid
            if not 'import_file' in self.env.context:
                # When importing a file, avoid recomputing the opening move for each account and do it at the end, for better performances
                self.company_id._auto_balance_opening_move()




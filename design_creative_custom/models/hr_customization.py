import time

from odoo import models, fields, api, _
from calendar import isleap
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class inherithremploye(models.Model):
    _inherit = 'hr.employee'

    bahrain_expact = fields.Selection([('Bahraini', 'Bahraini'), ('Expats', 'Expats')], string='Bahranis/Expacts', )
    muslim = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Muslim', )
    age = fields.Char(string="Age", compute='set_age_computed')
    dependent = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Dependent', )
    cpr_no = fields.Char(string="CPR NO")
    cpr_exp_date = fields.Date(string="CPR Expiry")
    passport_exp_date = fields.Date(string="Passport Expiry")
    rp_exp_date = fields.Date(string="RP Expiry")
    veh_alloted = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Vehicle Alloted')
    accomodation = fields.Selection([('YES', 'YES'), ('NO', 'NO')], string='Acomodation')

    ot_eligible = fields.Boolean(string="OT Eligible?", default=False)
    ot_weekday = fields.Boolean(string="OT Weekdays")
    ot_weekend = fields.Boolean(string="OT Weekends")

    ot_ramzan = fields.Boolean(string="OT Ramadan?")
    ot_ramzan_muslims = fields.Boolean(string="OT Ramadan muslims only?")

    sat_work = fields.Boolean(string="Saturday Workers?", default=True)
    sat_offic = fields.Boolean(string="Saturday officers?")

    manual_schedule = fields.Boolean(string="Manual schedule?")

    workschedule = fields.Selection(
        [('08:00-01:00|02:00-05:00', '08:00-01:00|02:00-05:00'), ('08:30-01:00|02:30-06:00', '08:30-01:00|02:30-06:00'),
         ('08:30|03:00', '08:30|03:00')],
        string="Select schedule")

    man_works_fhour = fields.Char("First shift start")
    man_works_fmins = fields.Char("First shift end")

    man_works_shour = fields.Char("Second shift start")
    man_works_smins = fields.Char("second shift end")

    @api.onchange('man_works_fhour', 'man_works_fmins', 'man_works_shour', 'man_works_smins')
    def onchangmanul_work(self):
        if self.man_works_fhour:
            try:
                time_obj_first_check_out = datetime.datetime.strptime(self.man_works_fhour, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.man_works_fmins:
            try:
                time_obj_first_check_out = datetime.datetime.strptime(self.man_works_fmins, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.man_works_shour:
            try:
                time_obj_first_check_out = datetime.datetime.strptime(self.man_works_shour, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.man_works_smins:
            try:
                time_obj_first_check_out = datetime.datetime.strptime(self.man_works_smins, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('workschedule')
    def onchangeschedule_work(self):
        if self.workschedule:
            if self.workschedule == '08:30|03:00' and self.ot_ramzan:
                pass
            elif self.ot_ramzan:
                raise UserError('Wrong schedule seclected')

    @api.onchange('ot_ramzan_muslims')
    def onchanotrmza_work(self):
        if self.ot_ramzan_muslims:
            if self.muslim:
                pass
            else:
                raise UserError('Cannot apply on Non-Muslim')

    @api.onchange('ot_ramzan')
    def oncrnana_work(self):
        if self.ot_ramzan:
            self.manual_schedule=False
            self.workschedule='08:30|03:00'

    def calculateAge(self, dob):
        today = date.today()
        try:
            birthday = dob.replace(year=today.year)

            # raised when birth date is February 29
        # and the current year is not a leap year
        except ValueError:
            birthday = dob.replace(year=today.year,
                                   month=dob.month + 1, day=1)

        if birthday > today:
            return today.year - dob.year - 1
        else:
            return today.year - dob.year

    def set_age_computed(self):
        if self.birthday:
            self.age = str(self.calculateAge(self.birthday))
        else:
            self.age = "N/A"

    # designation=fields.Many2one('employee.designation',)


class inheritcontracts(models.Model):
    _inherit = 'hr.contract'

    housing_allowance = fields.Float("Housing Allowance", default=0.00)
    travel_allowance = fields.Float("Travel Allowance", default=0.00)
    increment_Date = fields.Date(string="Increment Date")
    increment_Amount = fields.Float("Amount", default=0.00)
    leave_Status = fields.Selection(
        [('Active', 'Active'), ('Terminated', 'Terminated'), ('Resigned', 'Resigned'), ('Vacation', 'Vacation')],
        string='Leave Status', )
    leave_due = fields.Float("Leave Due", default=0.00)
    leave_amount = fields.Float("Leave Amount", default=0.00)
    total_work_experience = fields.Char(string="Total Work Experience")
    indemnity = fields.Char(string="Indemnity")
    tenure = fields.Char(string="Tenure")
    sponsorship = fields.Selection([('Design Creative', 'Design Creative'), ('Design Grafix', 'Design Grafix')],
                                   string='Sponsorship', )
    work_location = fields.Selection([('DG', 'DG'), ('DC', 'DC')], string='Work Location', )
    gosi_Salary_Deduction = fields.Float("GOSI Salery deduction", default=0.00)
    hourly_salery = fields.Float("Hourly salery", default=0.00)
    Misce_Allowance = fields.Float("Miscellaneous Allowance", default=0.00)
    OT = fields.Float("OT", default=0.00)
    OT1 = fields.Float("OT 1", default=0.00)
    OT2 = fields.Float("OT 2", default=0.00)
    OTw = fields.Float("OT(W)", default=0.00)

    p_salery = fields.Monetary(string="Salary")
    p_salery_pd = fields.Monetary(string='Salary / Day', digits=(16, 3), default=0.0, compute='salery_comp', store=True)
    p_salery_ph = fields.Monetary(string='Salary / Hour', digits=(16, 3), default=0.0, compute='salery_comp',
                                  store=True)

    department_id = fields.Many2one(related='employee_id.department_id', string="Department")

    # p_leave_salery=fields.Monetary(string='Leave Salary',digits=(16, 3))
    p_leave_salery_pd = fields.Monetary(string='Leave Salary / Day', digits=(16, 3), default=0.0, )
    p_leave_salery_ph = fields.Monetary(string='Leave Salary /  Hour', digits=(16, 3), default=0.0, )

    # p_ideminity=fields.Monetary(string='Ideminity',digits=(16, 3))
    p_ideminity_pd = fields.Monetary(string='Ideminity / Day', digits=(16, 4), default=0.0)
    p_ideminity_ph = fields.Monetary(string='Ideminity / hour', digits=(16, 4), default=0.0)

    p_airfair = fields.Monetary(string='Airfare', digits=(16, 3))
    p_airfair_pd = fields.Monetary(string='Airfare / Day', digits=(16, 3), default=0.0, store=True, compute='air_comp')
    p_airfair_ph = fields.Monetary(string='Airfare / hour', digits=(16, 3), default=0.0, store=True, compute='air_comp')

    p_lmra = fields.Monetary(string='Lmra', digits=(16, 3))
    p_lmra_pd = fields.Monetary(string='Lmra / Day', digits=(16, 3), default=0.0, store=True, compute='lmra_comp')
    p_lmra_ph = fields.Monetary(string='Lmra / Hour', digits=(16, 3), default=0.0, store=True, compute='lmra_comp')

    p_visa = fields.Monetary(string='Visa', digits=(16, 3))
    p_visa_pd = fields.Monetary(string='Visa / Day', digits=(16, 3), default=0.0, store=True, compute='visa_comp')
    p_visa_ph = fields.Monetary(string='Visa / hour', digits=(16, 3), default=0.0, store=True, compute='visa_comp')

    p_gosi_pd = fields.Monetary(string='Gosi / Day', digits=(16, 3), default=0.0)
    p_gosi_ph = fields.Monetary(string='Gosi / Hour', digits=(16, 3), default=0.0)
    grade = fields.Many2one('hr.grade', string="grade")
    final_hourly_rate = fields.Monetary('Final  / hourly rate', compute='get_hourly_final')
    final_day_rate = fields.Monetary('Final / Day rate', compute='get_hourly_final')

    gosi_salery = fields.Monetary(string='Gosi Salery', digits=(16, 3), default=0.0)
    gross_salery = fields.Monetary(string='Gross Salery', digits=(16, 3), compute='get_gross_salery')
    select_incrmnt = fields.Selection([('Basic', 'Basic'), ('Housing', 'Housing'), ('Travel', 'Travel')],
                                      string='Increment Type')
    select_decrement = fields.Selection([('Basic', 'Basic'), ('Housing', 'Housing'), ('Travel', 'Travel')],
                                        string='Decrement Type')
    do_incrmnt = fields.Boolean('Will Increment?', default=False)
    do_decre = fields.Boolean('Will Decrement?', default=False)

    @api.onchange('increment_Amount')
    def onchange_select_incrmnt(self):
        if self.do_incrmnt:
            if self.select_incrmnt == 'Basic':
                self.wage += self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_incrmnt == 'None':
                pass
            elif self.select_incrmnt == 'Housing':
                self.housing_allowance += self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_incrmnt == 'Travel':
                self.travel_allowance += self.increment_Amount
                self.increment_Amount = 0.0
        elif self.do_decre:
            if self.select_decrement == 'Basic':
                self.wage -= self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_decrement == 'Housing':
                self.housing_allowance -= self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_decrement == 'Travel':
                self.travel_allowance -= self.increment_Amount
                self.increment_Amount = 0.0

    @api.onchange('gosi_salery')
    def onchange_gosisalery(self):
        if self.gosi_salery:
            if self.employee_id.bahrain_expact == 'Bahraini':
                self.gosi_Salary_Deduction = (self.gosi_salery * 7) / 100
            else:
                self.gosi_Salary_Deduction = (self.gosi_salery * 1) / 100

    @api.depends('wage', 'housing_allowance', 'travel_allowance', 'increment_Amount', 'gosi_Salary_Deduction')
    def get_gross_salery(self):
        for rec in self:
            rec.gross_salery = (
                                       rec.wage + rec.housing_allowance + rec.travel_allowance + rec.increment_Amount) - rec.gosi_Salary_Deduction

    @api.depends('p_salery', 'p_airfair', 'p_lmra', 'p_visa')
    def get_hourly_final(self):
        for rec in self:
            rec.final_hourly_rate = rec.p_salery_ph + rec.p_leave_salery_ph + rec.p_airfair_ph + rec.p_ideminity_ph + rec.p_lmra_ph + rec.p_visa_ph \
                                    + rec.p_gosi_ph
            rec.final_day_rate = rec.p_salery_pd + rec.p_leave_salery_pd + rec.p_airfair_pd + rec.p_ideminity_pd + rec.p_lmra_pd + rec.p_visa_pd \
                                 + rec.p_gosi_pd

    @api.depends('p_salery')
    def salery_comp(self):
        for rec in self:
            if rec.p_salery:
                # leave calcualtion
                year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_leave_salery_pd = rec.p_salery / 366
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8

                    rec.p_ideminity_pd = rec.p_salery / 366
                    rec.p_ideminity_ph = rec.p_ideminity_pd / 8
                else:
                    rec.p_leave_salery_pd = rec.p_salery / 365
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8

                    rec.p_ideminity_pd = rec.p_salery / 365
                    rec.p_ideminity_ph = rec.p_ideminity_pd / 8

                # salery calculation
                rec.p_salery_pd = rec.p_salery / 30
                rec.p_salery_ph = rec.p_salery_pd / 8
                # Gosi calculation
                citizen = rec.employee_id.bahrain_expact

                if citizen == 'Expats':
                    rec.p_gosi_pd = ((rec.p_salery * 3) / 100) / 30
                    rec.p_gosi_ph = rec.p_gosi_pd / 8

                elif citizen == 'Bahraini':
                    rec.p_gosi_pd = ((rec.p_salery * 12) / 100) / 30
                    rec.p_gosi_ph = rec.p_gosi_pd / 8
                # indiminity calculation

    @api.depends('p_leave_salery')
    def leave_comp(self):
        for rec in self:
            if rec.p_leave_salery:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_leave_salery_pd = rec.p_leave_salery / 366
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8
                else:
                    rec.p_leave_salery_pd = rec.p_leave_salery / 365
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8

    @api.depends('p_airfair')
    def air_comp(self):
        for rec in self:
            if rec.p_airfair:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_airfair_pd = rec.p_airfair / 731
                    rec.p_airfair_ph = rec.p_airfair_pd / 8
                else:
                    rec.p_airfair_pd = rec.p_airfair / 730
                    rec.p_airfair_ph = rec.p_airfair_pd / 8

    # @api.depends('p_ideminity')
    # def ideminity_comp(self):
    #     for rec in self:
    #         if rec.p_ideminity:
    #             # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))
    #
    #             year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')
    #
    #             # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
    #             if isleap(int(year)):
    #                 rec.p_ideminity_pd = rec.p_ideminity / 366
    #                 rec.p_ideminity_ph = rec.p_ideminity_pd / 8
    #             else:
    #                 rec.p_ideminity_pd = rec.p_ideminity / 365
    #                 rec.p_ideminity_ph = rec.p_ideminity_pd / 8

    @api.depends('p_lmra')
    def lmra_comp(self):
        for rec in self:
            if rec.p_lmra:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                # year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                rec.p_lmra_pd = rec.p_lmra / 30
                rec.p_lmra_ph = rec.p_lmra_pd / 8

    @api.depends('p_visa')
    def visa_comp(self):
        for rec in self:
            if rec.p_visa:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_visa_pd = rec.p_visa / 731
                    rec.p_visa_ph = rec.p_visa_pd / 8
                else:
                    rec.p_visa_pd = rec.p_visa / 730
                    rec.p_visa_ph = rec.p_visa_pd / 8


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
                                                                      ('move_id', '=', opening_move.id),
                                                                      (field, '!=', False),
                                                                      (field, '!=',
                                                                       0.0)])  # 0.0 condition important for import

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


class hr_gradeclass(models.Model):
    _name = 'hr.grade'
    _rec_name = 'name'

    name = fields.Char(string="Name", compute='comp_name', store=True)
    grade = fields.Char(string="Grade", required=1)
    department = fields.Many2one('hr.department', string='Department', required=1)
    designation = fields.Many2one('hr.job', string='Designations', required=1)

    @api.depends('grade', 'department', 'designation')
    def comp_name(self):
        for rec in self:
            if rec.grade and rec.department and rec.designation:
                rec.name = rec.grade + '-' + rec.designation.name

    # @api.constrains('grade','department','designation')
    # def _check_name(self):
    #     for rec in self:
    #         record_exist = self.env['hr.grade'].search([('grade', '=', rec.grade),('department', '=', rec.department.id),('designation', '=', rec.designation.id)])
    #         if len(record_exist) > 1:
    #             raise UserError('Grade for selected department and designation already exist')

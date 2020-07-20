# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    date_of_join = fields.Date('Joining Date')
    resign=fields.Boolean(default=False,string="Resign?")
    terminate=fields.Boolean(default=False,string="Terminate?")
    runaway=fields.Boolean(default=False,string="Runaway?")

    date_of_leave = fields.Date('Leave/Terminate Date')
    bank_name = fields.Char(string="Bank Name")
    Ac_number = fields.Char(string="A/C Number")

    consider_days = fields.Integer(string="Total Work Day(s)", compute="_get_days_calculation")
    absents = fields.Integer(string="Absents", compute="_get_days_calculation")

    def _get_days_calculation(self):
        t_date_month=datetime.datetime.now().date().month
        for dta in self:
            recor = self.env['attendance.custom'].search(
                [
                 ('employee_id', '=',
                  dta.id)
                 ])
            total=0
            absnt=0

            for rec in recor:
                if rec.attendance_date.month == t_date_month:
                    total+=1
                    if rec.absent:
                        absnt+=1
            dta.absents = absnt
            if not total <= 0:
                dta.consider_days=total - absnt
            else:
                dta.consider_days=0




    @api.onchange('resign')
    def resign_lv(self):
        if self.resign:
            self.active=False
        else:
            self.active=True


class HrPayslip_inherits(models.Model):
    _inherit = "hr.payslip"

    total_work_day = fields.Integer(string="Total Work Day(s)", compute="_get_days_calculation")
    absents = fields.Integer(string="Absents", compute="_get_days_calculation")
    consider_days = fields.Integer(string="Consider Days", compute="_get_days_calculation")

    @api.depends('date_from', 'date_to','employee_id')
    def _get_days_calculation(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.employee_id:
                total = self.env['attendance.custom'].search_count(
                    [('attendance_date', '>=', rec.date_from), ('attendance_date', '<=', rec.date_to),
                     ('employee_id', '=',
                      rec.employee_id.id)
                     ])
                # if rec.date_to.day == 31:
                #     if total>30:
                #        total-=1

                df = rec.date_from
                dt = rec.date_to
                absnt=0

                delta = datetime.timedelta(days=1)
                while df <= dt:
                    print(df)
                    check_attendence = self.env['attendance.custom'].search(
                        [('absent','=',True),
                            ('attendance_date', '=', df), ('employee_id', '=', rec.employee_id.id)])
                    if check_attendence:
                        absnt+=1
                    df += delta



                rec.total_work_day= total
                rec.absents = absnt
                if not total <= 0:
                    rec.consider_days=total - absnt
                else:
                    rec.consider_days=0
            else:
                rec.consider_days = 30
                rec.total_work_day=30
                rec.absents=0




    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            df = payslip.date_from
            dt = payslip.date_to
            delta = datetime.timedelta(days=1)
            while df <= dt:
                print(df)
                check_attendence = self.env['attendance.custom'].search(
                    [('attendance_date', '=', df), ('employee_id', '=', payslip.employee_id.id)])
                if not check_attendence:
                    raise UserError(
                        _("Attendance of %s not found in system . Please mark attendance first") % (str(df)))
                df += delta

            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
        return True

class leaveallocation_inherit(models.Model):
    _inherit = "hr.leave.allocation"


    def update_paid_days(self):
        for rec in self.search([]):
            if rec.holiday_status_id.name == 'Paid Time Off':
                rec.number_of_days +=2.5

class HrPayslipEmployees_inheritx(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id)]

    def _get_employees(self):
        # YTI check dates too
        t_date_month=datetime.datetime.now().date().month

        emp=self.env['hr.employee']
        lst=self.env['hr.employee'].search(self._get_available_contracts_domain())
        for rec in lst:
            line=rec.slip_ids.filtered(lambda r:r.date_from.month == t_date_month)
            if not line:
                emp+=rec

        return emp



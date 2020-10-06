# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

import datetime
from odoo.exceptions import UserError, ValidationError


class Employee(models.Model):
    _inherit = 'hr.contract'

    def get_latein_amount(self, employee_id, basic_salary, from_date, to_date):
        # so get attendance between those date
        # apply_latein_deduction and exception_approved, count the numbers and if yes then get then divide it by 2, so you have to deduct this day salary
        # get basic salary half day calulcations so its ok get it by multiply

        attendance_days_count = self.env['attendance.custom'].search_count(
            [('employee_id', '=', employee_id), ('attendance_date', '>=', from_date),
             ('attendance_date', '<=', to_date),('exception_approved', '=', False),
             ('apply_latein_deduction','=', True)])
        if attendance_days_count:
            num_days_deducted = attendance_days_count / 2
            return (basic_salary/30) * num_days_deducted
        else:
            return 0

    def get_perminute_rate(self, basic_salary):
        perday = basic_salary / 30
        working_hours = perday / 8
        perminute = working_hours / 60
        return perminute


    @api.model
    def get_ot_125(self, employee_id, basic_salary, from_date, to_date):
        attendance_rec = self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '>=', from_date),('allow_viewoto','=',True),
             ('attendance_date', '<=', to_date), ('ot_125', '!=', None)])
        attendance_rec_minutes = 0
        if attendance_rec:
            print(attendance_rec[0])
            for rec in range(len(attendance_rec)):
                 attendance_rec_minutes += int(attendance_rec[rec].ot_125.split(':')[0]) * 60 + int(attendance_rec[rec].ot_125.split(':')[1])
            # inke minuts ko sum kr ke perminute rate * 1.25
            perminute = self.get_perminute_rate(basic_salary)
            return attendance_rec_minutes * 1.25 * perminute
        else:
            return 0

    @api.model
    def get_ot_15(self, employee_id, basic_salary, from_date, to_date):
        attendance_rec = self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '>=', from_date),('allow_viewotf','=',True),
             ('attendance_date', '<=', to_date), ('ot_125', '!=', None)])
        attendance_rec_minutes = 0
        if attendance_rec:
            print(attendance_rec[0])
            for rec in range(len(attendance_rec)):
                attendance_rec_minutes += int(attendance_rec[rec].ot_15.split(':')[0]) * 60 + int(
                    attendance_rec[rec].ot_15.split(':')[1])
            # inke minuts ko sum kr ke perminute rate * 1.25
            perminute = self.get_perminute_rate(basic_salary)
            return attendance_rec_minutes * 1.50 * perminute
        else:
            return 0

    # @api.model
    # def comp_gross_salery(self,basic_salary,alw,payslip):
    #     if payslip.employee_id:
    #         df = payslip.date_from
    #         dt = payslip.date_to
    #         absnt = 0
    #
    #         delta = datetime.timedelta(days=1)
    #         while df <= dt:
    #             print(df)
    #             check_attendence = self.env['attendance.custom'].search(
    #                 [('absent', '=',True),('attendance_date', '=', df), ('employee_id', '=', payslip.employee_id)])
    #             if check_attendence:
    #                 absnt += 1
    #             df += delta
    #
    #         if absnt == 0:
    #             return basic_salary+alw
    #         else:
    #             return  ((basic_salary + alw)/30)*absnt
    #     else:
    #         return 0



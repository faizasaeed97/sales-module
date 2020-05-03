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


class Attendance(models.Model):
    _name = 'attendance.custom'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', required=True)
    roll_number = fields.Char(related='employee_id.identification_id')

    attendance_date = fields.Date(string='Attendance Date', required=True,default=fields.Date.context_today)
    job_title = fields.Char(string='hr.job',compute='get_jobtitle')
    status = fields.Char(string='Status')
    custom_ID = fields.Char(string='ID')
    title = fields.Char(string='Title')

    first_check_in = fields.Char(string='Check In(1st)')
    first_check_out = fields.Char(string='Check Out(1st)')
    first_shift_total_hours = fields.Char(string='Hrs(1st)')
    working = fields.Char(string='Working')
    second_check_in = fields.Char(string='Check In(2nd)')
    second_check_out = fields.Char(string='Check Out(2nd)')
    second_shift_total_hours = fields.Char(string='Hrs(2nd)')
    job_code = fields.Char(string='JobCode')
    site = fields.Char(string='Site')
    late_in = fields.Char(string='Late In')
    early_in = fields.Char(string='Early In')
    early_out = fields.Char(string='Early Out')
    ot_125 = fields.Char(string='OT 125')
    small_ot = fields.Char(string='Small OT')
    no_attend = fields.Char(string='No Attend')
    ignored = fields.Char(string='Ingored')

    @api.depends('employee_id')
    def get_jobtitle(self):
        for rec in self:
            if rec.employee_id:
                jobtt=self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id)],limit=1)
                if jobtt:
                    if jobtt.grade:
                        rec.job_title = jobtt.grade.designation.name
                    else:
                        rec.job_title = None
                else:
                    rec.job_title=None
            else:
                rec.job_title=None


    @api.onchange('first_check_in', 'first_check_out')
    def onchangefirst_checkin_checkout(self):
        if self.first_check_in:
            try:
                time_obj_first_check_in = datetime.datetime.strptime(self.first_check_in, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.first_check_out:
            try:
                time_obj_first_check_out = datetime.datetime.strptime(self.first_check_out, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

        if self.first_check_in and self.first_check_out:
            self.first_shift_total_hours = str(time_obj_first_check_out - time_obj_first_check_in).split(":")[0] + ':' \
                                           + str(time_obj_first_check_out - time_obj_first_check_in).split(":")[1]

    @api.onchange('second_check_in', 'second_check_out')
    def onchangesecond_checkin_checkout(self):
        if self.second_check_in:
            try:
                time_obj_second_check_in = datetime.datetime.strptime(self.second_check_in, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.second_check_out:
            try:
                time_obj_second_check_out = datetime.datetime.strptime(self.second_check_out, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

        if self.second_check_in and self.second_check_out:
            self.second_shift_total_hours = str(time_obj_second_check_out - time_obj_second_check_in).split(":")[
                                                0] + ':' \
                                            + str(time_obj_second_check_out - time_obj_second_check_in).split(":")[1]

    @api.onchange('first_shift_total_hours', 'second_shift_total_hours')
    def get_workingtime(self):
        sum = 0
        if self.first_shift_total_hours:
            try:
                time_obj_1st_shifttotal = datetime.datetime.strptime(self.first_shift_total_hours, '%H:%M')
                a = dt.timedelta(hours=int(self.first_shift_total_hours.split(":")[0]),
                                 minutes=int(self.first_shift_total_hours.split(":")[1]))

            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

        if self.second_shift_total_hours:
            try:
                time_obj_2nd_shifttotal = datetime.datetime.strptime(self.second_shift_total_hours, '%H:%M')
                b = dt.timedelta(hours=int(self.second_shift_total_hours.split(":")[0]),
                                 minutes=int(self.second_shift_total_hours.split(":")[1]))

            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

        if self.first_shift_total_hours and self.second_shift_total_hours:
            self.working= a+b

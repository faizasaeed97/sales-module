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



class department(models.Model):
    _inherit = 'hr.department'

    st_checkin = fields.Char(string='Check In')
    st_checkout= fields.Char(string='Checkout')
    grace_time = fields.Char(string='Grace Time')

    @api.onchange('st_checkin')
    def onchange_checkin(self):
        if self.st_checkin:
            try:
                datetime.datetime.strptime(self.st_checkin, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('st_checkout')
    def onchange_checkout(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.st_checkout, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('grace_time')
    def onchange_grace_time(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.grace_time, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))


class Employee(models.Model):
    _inherit = 'hr.employee'

    st_checkin = fields.Char(string='Check In')
    st_checkout= fields.Char(string='Checkout')
    grace_time = fields.Char(string='Grace Time')

    @api.onchange('st_checkin')
    def onchange_checkin(self):
        if self.st_checkin:
            try:
                datetime.datetime.strptime(self.st_checkin, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('st_checkout')
    def onchange_checkout(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.st_checkout, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('grace_time')
    def onchange_grace_time(self):
        if self.st_checkout:
            try:
                datetime.datetime.strptime(self.grace_time, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('department_id')
    def onchange_dept(self):
        if self.department_id:
            self.st_checkin=self.department_id.st_checkin
            self.st_checkout=self.department_id.st_checkout
            self.grace_time=self.department_id.grace_time

class Attendance(models.Model):
    _name = 'attendance.custom'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', required=True)
    roll_number = fields.Char(related='employee_id.identification_id')

    attendance_date = fields.Date(string='Attendance Date', required=True, default=fields.Date.context_today)
    job_title = fields.Char(string='Job Title', compute='get_jobtitle')
    status = fields.Char(string='Status')
    custom_ID = fields.Char(string='ID')
    title = fields.Char(string='Title')

    first_check_in = fields.Char(string='Check In(1st)')
    first_check_out = fields.Char(string='Check Out(1st)')
    first_shift_total_hours = fields.Char(compute='onchangefirst_checkin_checkout', string='Hrs(1st)')
    working = fields.Char(compute='get_workingtime', string='Working')
    second_check_in = fields.Char(string='Check In(2nd)')
    second_check_out = fields.Char(string='Check Out(2nd)')
    second_shift_total_hours = fields.Char(compute='onchangesecond_checkin_checkout', string='Hrs(2nd)')
    job_code = fields.Char(string='JobCode')
    site = fields.Char(string='Site')
    late_in = fields.Char(string='Late In')
    early_in = fields.Char(string='Early In')
    early_out = fields.Char(string='Early Out')
    ot_125 = fields.Char(string='OT 1.25', compute='get_ot_hours')
    ot_15 = fields.Char(string='OT 1.5', compute='get_ot_hours')
    no_attend = fields.Char(string='No Attend')
    ignored = fields.Char(string='Ingored')
    exception_approved=fields.Boolean(string='Exception Approved')
    apply_latein_deduction = fields.Boolean(compute='apply_latein',store=True,string='Apply Latein deduction')
    sick_leave=fields.Boolean(string="Sick leave",default=False)
    absent=fields.Boolean(string="Absent",default=False)
    sick_from=fields.Date(string="Leave From")
    sick_to=fields.Date(string="Leave To")

    @api.model
    def create(self, vals):
        attend = super(Attendance, self).create(vals)
        check = self.search([('employee_id','=',attend.employee_id.id),('sick_leave','=',True)])
        for rec in check:
            if rec.attendance_date.month == attend.attendance_date.month:
                print("-===============>|GOT IT")
                if attend.attendance_date.day >= rec.sick_from.day and  attend.attendance_date.day <= rec.sick_to.day:
                    print("-===============>|WAHHHH IT")
                    attend.sick_leave=True
                    attend.sick_from=rec.sick_from
                    attend.sick_to = rec.sick_to

        return attend

    def get_minute_hmformat(self,seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%d:%02d" % (hour, minutes)

    @api.depends('first_check_in')
    def apply_latein(self):
        #get from employee defination check in , so get the difference after checkin
        for record in self:
            employee_checkin = record.employee_id.st_checkin
            if record.first_check_in and employee_checkin:
                # check the difference
                # if 15 min allow, he come even seconds late, what we can do mark him apply late in logic

                FMT = '%H:%M'
                print(record.first_check_in)
                tdelta =datetime.datetime.strptime(record.first_check_in, FMT)-datetime.datetime.strptime(record.employee_id.st_checkin, FMT)
                # check if difference greater than 15 minute
                # also include grace time
                if tdelta.days<0:
                    record.apply_latein_deduction=False
                if not tdelta.days<0:
                   #convert H:M to seconds and compare it with grace if its greater it means deduction apply
                   seconds_difference_checkin=tdelta.seconds
                   grace_time_seconds=(datetime.datetime.strptime(record.employee_id.grace_time, FMT).hour)*60*60+\
                                      (datetime.datetime.strptime(record.employee_id.grace_time, FMT).minute)*60

                   if seconds_difference_checkin>grace_time_seconds:
                       record.apply_latein_deduction=True
                   else:
                       record.apply_latein_deduction = False
            else:
                record.apply_latein_deduction=False


    @api.depends('working','attendance_date')
    def get_ot_hours(self):
        # if day is friday so what the rate is 1.50
        # first step get the OT hours, check if OT hours more than 2 or less, if its more than two consider 1.50 also otherwise 1,25
        for record in self:
            if record.working and record.attendance_date:
                # here we get Overall OT hours
                record.ot_15 = '00:00'
                record.ot_125 = '00:00'
                ot_minute = (int(record.working.split(':')[0])*60 + int(record.working.split(':')[1])) - 480
                day =record.attendance_date.strftime('%A')
                if ot_minute>0:
                    if day=='Friday':
                        record.ot_15 = record.get_minute_hmformat(ot_minute*60)
                    else:
                        if ot_minute <= 120:
                            # get the difference minute after 120 and update ot1.5
                            record.ot_125 = record.get_minute_hmformat(ot_minute*60)

                        if ot_minute > 120:
                            # get the difference minute after 120 and update ot1.5
                            record.ot_15 = record.get_minute_hmformat((ot_minute - 120)*60)
                            record.ot_125=record.get_minute_hmformat(120*60)

    @api.depends('employee_id')
    def get_jobtitle(self):
        for rec in self:
            if rec.employee_id:
                jobtt = rec.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id)], limit=1)
                if jobtt:
                    # if jobtt.grade:
                    #     rec.job_title = jobtt.grade.designation.name
                    # else:
                    #     rec.job_title = None
                    rec.job_title = None
                else:
                    rec.job_title = None
            else:
                rec.job_title = None


    @api.depends('first_check_in', 'first_check_out')
    def onchangefirst_checkin_checkout(self):
        for rec in self:

            if rec.first_check_in:
                try:
                    time_obj_first_check_in = datetime.datetime.strptime(rec.first_check_in, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))
            if rec.first_check_out:
                try:
                    time_obj_first_check_out = datetime.datetime.strptime(rec.first_check_out, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))

            if rec.first_check_in and rec.first_check_out:
                rec.first_shift_total_hours = str(time_obj_first_check_out - time_obj_first_check_in).split(":")[0] + ':' \
                                               + str(time_obj_first_check_out - time_obj_first_check_in).split(":")[1]
            else:
                rec.first_shift_total_hours = '00:00'


    @api.depends('second_check_in', 'second_check_out')
    def onchangesecond_checkin_checkout(self):
        for rec in self:

            if rec.second_check_in:
                try:
                    time_obj_second_check_in = datetime.datetime.strptime(rec.second_check_in, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))
            if rec.second_check_out:
                try:
                    time_obj_second_check_out = datetime.datetime.strptime(rec.second_check_out, '%H:%M')
                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))

            if rec.second_check_in and rec.second_check_out:
                rec.second_shift_total_hours = str(time_obj_second_check_out - time_obj_second_check_in).split(":")[
                                                    0] + ':' \
                                                + str(time_obj_second_check_out - time_obj_second_check_in).split(":")[1]
            else:
                rec.second_shift_total_hours = '00:00'

    @api.depends('first_shift_total_hours', 'second_shift_total_hours')
    def get_workingtime(self):
        for rec in self:
            sum = 0
            if rec.first_shift_total_hours:
                try:
                    time_obj_1st_shifttotal = datetime.datetime.strptime(rec.first_shift_total_hours, '%H:%M')
                    a = dt.timedelta(hours=int(rec.first_shift_total_hours.split(":")[0]),
                                     minutes=int(rec.first_shift_total_hours.split(":")[1]))

                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))

            if rec.second_shift_total_hours:
                try:
                    time_obj_2nd_shifttotal = datetime.datetime.strptime(rec.second_shift_total_hours, '%H:%M')
                    b = dt.timedelta(hours=int(rec.second_shift_total_hours.split(":")[0]),
                                     minutes=int(rec.second_shift_total_hours.split(":")[1]))

                except:
                    raise ValidationError(_("Follow Correct Format 00:00"))

            if rec.first_shift_total_hours and rec.second_shift_total_hours:
                rec.working = str(a + b).split(':')[0] + ':' + str(a + b).split(':')[1]




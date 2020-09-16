from collections import defaultdict

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class hr_expiry(models.Model):
    _name = 'hr.expiry.alert'

    name = fields.Char(string="name")
    reason=fields.Char(compute="default_value",string="reason",store=True)
    alert = fields.One2many('hr.expiry.lineitem', 'new_id', String="Alert")
    @api.depends('name')
    def default_value(self):
        if self.name:
              self.reason=str("expired Employee List") + self.name

class line_item(models.Model):
    _name = 'hr.expiry.lineitem'

    new_id = fields.Many2one('hr.expiry.alert', string="Type ID")
    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    reason = fields.Char(String="Reason")
    date = fields.Date(string ="Date")
    current_date = fields.Date(string='Your string', default=datetime.today())
    no_of_days = fields.Integer(string = "No. of Days")


    @api.onchange('date')
    def calculate_date(self):
        if self.date and self.current_date:
             d1 = datetime.strptime(str(self.date), '%Y-%m-%d')
             d2 = datetime.strptime(str(self.current_date), '%Y-%m-%d')
             d3 = d2 - d1
             self.no_of_days= int(d3.days)
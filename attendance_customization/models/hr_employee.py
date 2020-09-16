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

    name = fields.Char(String="Name")
    alert = fields.One2many('hr.expiry.lineitem', 'new_id', String="Alert")


class line_item(models.Model):
    _name = 'hr.expiry.lineitem'

    new_id = fields.Many2one('hr.expiry.alert', string="Type ID")
    employee_id = fields.Many2one('hr.employee', string="Employee ID")
    reason = fields.Char(String="Reason")
    date = fields.Date (string ="Date")
    no_of_days = fields.Int (string = "No. of Days")

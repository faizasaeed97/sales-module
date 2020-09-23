from collections import defaultdict

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict
from datetime import datetime, date, time, timedelta
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class hr_calendar_leave(models.Model):
    _name = 'hr.calendar.leave'
    _rec_name='name'

    name = fields.Char(String="Name",default="Leave roadmap",readonly=1)
    leave = fields.One2many('hr.leave.lineitem', 'new_id_second', String="Leave")


class line_item_two(models.Model):
    _name = 'hr.leave.lineitem'

    new_id_second = fields.Many2one('hr.calendar.leave', string="Type ID")
    leave_name = fields.Char(string="Leave name")
    leave_date = fields.Date(string="Date")

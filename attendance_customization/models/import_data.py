from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime as dt

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
import time  as tm
import datetime
from odoo.exceptions import UserError, ValidationError
import base64
from xlrd import open_workbook


class ImportAttendance(models.TransientModel):
    _name = 'attendance.import'

    file = fields.Binary(string='File Upload')

    def get_time(self, x):
        if x:
            x = int(x * 24 * 3600)  # convert to number of seconds
            minute=x/60
            hour=minute/60
            my_time = time(x // 3600, (x % 3600) // 60, x % 60)  # hours, minutes, seconds
            print(type(my_time))
            return str(my_time.hour)+':'+str(my_time.minute)



    def is_attendance_exist_sameday(self, employee_id, attendance_date):
        return self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '=', attendance_date)])

    def action_import_create_attendance(self):
        if self.file:
            wb = open_workbook(file_contents=base64.decodestring(self.file))
            sheet = wb.sheet_by_index(0)
            purchase_array = []

            # Row 2 , Column1
            attendance_list = []
            for row in range(1, sheet.nrows):
                attendance_dict = {}
                id_no = int(sheet.cell(row, 0).value)
                emp=self.env['hr.employee'].search([('identification_id','=',id_no)])
                attendance_date = sheet.cell(row, 1).value
                first_in = sheet.cell(row, 7).value
                first_out = sheet.cell(row, 8).value
                second_in = sheet.cell(row, 12).value
                second_out = sheet.cell(row, 13).value
                exception_approved= sheet.cell(row, 26).value
                attendance_dict['employee_id'] = emp.id
                attendance_dict['attendance_date'] = attendance_date
                attendance_dict['first_in'] = self.get_time(first_in)
                attendance_dict['first_out'] = self.get_time(first_out)
                attendance_dict['second_in'] = self.get_time(second_in)
                attendance_dict['second_out'] = self.get_time(second_out)
                attendance_dict['exception_approved'] = exception_approved
                attendance_list.append(attendance_dict)

            if attendance_list:
                # create attendance records for each one, check if attendance not found on same date, else give error already exist.
                for obj in attendance_list:
                    if obj['employee_id'] and obj['attendance_date'] and not \
                            self.is_attendance_exist_sameday(obj['employee_id'], obj['attendance_date']):
                        print('yes..',obj['employee_id'],obj['attendance_date'])
                        self.env['attendance.custom'].create({'employee_id': obj['employee_id'],
                                                              'attendance_date':datetime.datetime.strptime(str(obj['attendance_date']), '%d/%m/%Y'),
                                                              'first_check_in': obj['first_in'],
                                                              'first_check_out': obj['first_out'],
                                                              'second_check_in': obj['second_in'],
                                                              'second_check_out': obj['second_out'],'exception_approved':obj['exception_approved']})

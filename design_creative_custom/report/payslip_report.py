# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class pyslippytDetails(models.TransientModel):
    _name = 'payslip.summery.details'
    _description = "Project Report Details"

    month = fields.Selection(
        [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul')
            , ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')], 'Month',
        required=True)
    year = fields.Selection([(str(num), str(num)) for num in range(2000, (datetime.now().year) + 20)], 'Year',
                            required=True)

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def print_report(self):
        plist = []
        month = self.month
        year = self.year

        dept = self.env['hr.department'].search(
            [])

        for rec in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = rec.name
            plist.append(dix)

            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            for dec in emps:
                slip = self.env['hr.payslip'].search(
                    [('contract_id', '=', dec.contract_id.id)])
                for slp in slip:
                    if slp.date_from.month == int(month) and slp.date_from.year == int(year):
                        deduc = 0.0
                        ot_tot = 0.0
                        dix = {}
                        dix['data'] = 'nd'
                        dix['div'] = rec.name
                        dix['date'] = dec.date_of_join
                        dix['emp'] = dec.name
                        dix['id'] = dec.identification_id

                        dix['worked'] = slp.consider_days
                        dix['absent'] = slp.absents

                        for nep in slp.line_ids:
                            if nep.category_id.name == "Deduction":
                                deduc += nep.total
                            if nep.name in ["OT(1.5) Allowance", "OT (125) Allowance"]:
                                ot_tot += nep.total

                            dix[nep.name] = nep.total
                        dix['deduc'] = deduc
                        dix['ot_tot'] = ot_tot

                        plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'month': self.month,
                'year': self.year,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.employee_payslip_report_xlsx_id').report_action(self, data=data)


class EmployeePayslipReportExcel(models.AbstractModel):
    _name = 'report.design_creative_custom.report_xlsx'
    # _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):

        month = lines['form']['month']
        year = lines['form']['year']
        dta = lines['form']['dta']

        sign_head = workbook.add_format({
            "bold": 1,
            "border": 0,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '12',

        })

        std_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'navy',
            'font_size': '10',
        })

        format2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'blue',
            'font_size': '30',
        })

        sheet = workbook.add_worksheet('MasterSheet')

        sheet.merge_range(2, 5, 3, 10, "Payslip report", format2)


        row = 4
        col = 0

        sheet.merge_range(row, col, "ID", sign_head)

        sheet.set_column(row, col+1, 400)
        sheet.write(row, col + 1, "Name", sign_head)
        sheet.write(row, col + 2, "Date of join", sign_head)
        sheet.write(row, col + 3, "Working", sign_head)
        sheet.write(row, col + 4, "Leave/sick", sign_head)

        sheet.write(row, col + 5, "Basic", sign_head)
        sheet.write(row, col + 6, "Travel", sign_head)
        sheet.write(row, col + 7, "housing", sign_head)

        sheet.write(row, col + 8, "OT1", sign_head)
        sheet.write(row, col + 9, "OT2", sign_head)
        sheet.write(row, col + 10, "OT total", sign_head)

        sheet.write(row, col + 11, "Loan", sign_head)
        sheet.write(row, col + 12, "hourly Deduct", sign_head)

        sheet.write(row, col + 13, "Gosi salery", sign_head)
        sheet.write(row, col + 14, "Gross", sign_head)
        sheet.write(row, col + 15, "Deduction", sign_head)

        sheet.write(row, col + 16, "Net Pay", sign_head)

        row = 6
        col = 0
        for rec in dta:

            if rec.get('data') == 'd':
                sheet.set_column(row+1, col, 20)
                sheet.write(row+1, col, rec.get('div'), sign_head)
                # sheet.write(row + 1, col + 1, rec.get('ID'), std_heading)
                # sheet.write(row + 1, col + 2, rec.get('ID'), std_heading)
                # sheet.write(row + 1, col + 3, rec.get('ID'), std_heading)
                row+=1

            if rec.get('data') == 'nd':
                sheet.set_column(row , col, 10)
                sheet.write(row, col, rec.get('id'), std_heading)

                sheet.set_column(row, col+1, 400)
                sheet.write(row, col + 1, rec.get('emp'), std_heading)

                sheet.set_column(row, col+2, 15)
                sheet.write(row, col + 2, rec.get('date'), std_heading)

                sheet.set_column(row, col+3, 10)
                sheet.write(row, col + 3, rec.get('worked'), std_heading)

                sheet.set_column(row, col+4, 10)
                sheet.write(row, col + 4, rec.get('absent'), std_heading)

                sheet.set_column(row, col+5, 10)
                sheet.write(row, col + 5, rec.get('Basic Salary'), std_heading)
                sheet.set_column(row, col+6, 10)
                sheet.write(row, col + 6, rec.get('Travel Allowance'), std_heading)
                sheet.set_column(row, col+7, 10)
                sheet.write(row, col + 7, rec.get('Housing Allowance'), std_heading)

                sheet.set_column(row, col+8, 15)
                sheet.write(row, col + 8, rec.get('OT (125) Allowance'), std_heading)
                sheet.set_column(row, col+9, 15)
                sheet.write(row, col + 9, rec.get('OT(1.5) Allowance'), std_heading)
                sheet.set_column(row, col+10, 10)
                sheet.write(row, col + 10, rec.get('ot_tot'), std_heading)

                sheet.set_column(row, col+11, 10)
                sheet.write(row, col + 11, rec.get('Loan Earning'), std_heading)
                sheet.set_column(row, col+12, 15)
                sheet.write(row, col + 12, rec.get('Late In Deduction'), std_heading)
                sheet.set_column(row, col+13, 15)

                sheet.write(row, col + 13, rec.get('Gosi Deduction'), std_heading)
                sheet.set_column(row, col+14, 10)
                sheet.write(row, col + 14, rec.get('Gross'), std_heading)
                sheet.set_column(row, col+15, 10)
                sheet.write(row, col + 15, rec.get('deduc'), std_heading)
                sheet.set_column(row, col+16, 10)

                sheet.write(row, col + 16, rec.get('Net Salary'), std_heading)

            row += 1

        # sheet.merge_range(row1, col, row1+4, col+4,sign_admin , std_heading2)

        # for rec in data.employee_id:
        #     sheet.write(row, col, 'Employee ID', main_heading)
        #     sheet.write_string(row, col + 1, str(rec.employee_code), main_heading)
        #     sheet.write(row, col + 2, 'Employee Name', main_heading)
        #     sheet.write_string(row, col + 3, str(rec.name), main_heading)
        #     sheet.write(row + 1, col, 'Job Position', main_heading)
        #     sheet.write_string(row + 1, col + 1, str(rec.job_id.name), main_heading)
        #     sheet.write(row + 1, col + 2, 'Joining Date', main_heading)
        #     sheet.write_string(row + 1, col + 3, rec.bsgjoining_date.strftime("%m/%d/%Y"))
        #     emp_payslip = self.env['hr.payslip'].search(
        #         [('employee_id', '=', rec.id), ('date_from', '<=', data.to_date),
        #          ('date_to', '>', data.from_date)])
        #     row += 3
        #     list_dict = []
        #     if emp_payslip:
        #         rule_dict = OrderedDict.fromkeys((rule.name for payslip in emp_payslip for rule in payslip.line_ids),
        #                                          0.0)
        #         rule_dict.move_to_end('Net Salary')
        #         sheet.write(row, col, 'Payslip Name', main_heading2)
        #         col += 1
        #         for rule_name in rule_dict:
        #             sheet.write_string(row, col, rule_name, main_heading2)
        #             col += 1
        #         row += 1
        #         col = 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

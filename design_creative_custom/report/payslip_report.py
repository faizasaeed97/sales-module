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
        grand=0.0

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
                dix = {}
                if slip:
                    for slp in slip:
                        if slp.date_from.month == int(month) and slp.date_from.year == int(year):
                            deduc = 0.0
                            ot_tot = 0.0

                            dix['data'] = 'nd'
                            dix['div'] = rec.name
                            dix['date'] = dec.date_of_join
                            dix['emp'] = dec.name
                            dix['id'] = dec.identification_id

                            dix['worked'] = slp.consider_days
                            dix['absent'] = slp.absents
                            dix['desig'] = dec.contract_id.grade.designation.name


                            for nep in slp.line_ids:
                                if nep.category_id.name == "Deduction":
                                    deduc += nep.total
                                if nep.name in ["OT(1.5) Allowance", "OT (125) Allowance"]:
                                    ot_tot += nep.total
                                if nep.name == 'Net Salary':
                                    grand+=nep.total

                                dix[nep.name] = nep.total
                            dix['deduc'] = deduc
                            dix['ot_tot'] = ot_tot
                        else:
                            dix['data'] = 'nd'
                            dix['div'] = rec.name
                            dix['date'] = dec.date_of_join
                            dix['emp'] = dec.name
                            dix['id'] = dec.identification_id


                else:
                    dix['data'] = 'nd'
                    dix['div'] = rec.name
                    dix['date'] = dec.date_of_join
                    dix['emp'] = dec.name
                    dix['id'] = dec.identification_id

                plist.append(dix)
        plist.append(
            {'data': 'n', 'grand': grand})

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'month': self.month,
                'year': self.year,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.pyslipxc_payslip_report_xlsx_id').report_action(self, data=data)


class pylsiprelipReportExcel(models.AbstractModel):
    _name = 'report.design_creative_custom.report_xlsx_ciew'
    # _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):

        month = lines['form']['month']
        year = lines['form']['year']
        dta = lines['form']['dta']

        sign_head_grand = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'blue',
            'font_size': '12',

        })

        sign_head = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '11',

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
            'font_size': '25',
        })

        sheet = workbook.add_worksheet('MasterSheet')

        sheet.merge_range(2, 5, 3, 10, "Payslip report", format2)

        sheet.merge_range(2, 1, 2, 2, "Month", sign_head)
        sheet.merge_range(3, 1, 3, 2, "Year", sign_head)

        sheet.merge_range(2, 3, 2, 4, month, std_heading)
        sheet.merge_range(3, 3, 3, 4, year, std_heading)



        row = 4
        col = 0
        sheet.set_column(row, col , 30)
        sheet.write(row, col, "Roll#", sign_head)

        sheet.set_column(row, col+1, 40)
        sheet.write(row, col + 1, "Name", sign_head)
        sheet.set_column(row, col+2, 30)
        sheet.write(row, col + 2, "Date of Join", sign_head)
        sheet.set_column(row, col+3, 30)

        sheet.write(row, col + 3, "Designation", sign_head)

        sheet.write(row, col + 4, "Worked", sign_head)
        sheet.write(row, col + 5, "Leave/sick", sign_head)

        sheet.write(row, col + 6, "Basic Salary", sign_head)
        sheet.write(row, col + 7, "Travel Allowance", sign_head)
        sheet.write(row, col + 8, "Housing Allowance", sign_head)

        sheet.write(row, col + 9, "OT1", sign_head)
        sheet.write(row, col + 10, "OT2", sign_head)
        sheet.write(row, col + 11, "Total OT", sign_head)

        sheet.write(row, col + 12, "Loan", sign_head)
        sheet.write(row, col + 13, "Hours Deduction", sign_head)

        sheet.write(row, col + 14, "GOSI Salary deductions", sign_head)
        sheet.write(row, col + 15, "Gross Pay", sign_head)
        sheet.write(row, col + 16, "Deduction", sign_head)

        sheet.write(row, col + 17, "Net Pay", sign_head)

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

            if rec.get('data') == 'n':
                sheet.write(row+1, 0, "Grand Total", sign_head_grand)

                sheet.set_column(row + 1, col, 20)
                sheet.write(row + 1, col+17, rec.get('grand'), sign_head_grand)

            if rec.get('data') == 'nd':
                sheet.set_column(row , col, 10)
                sheet.write(row, col, rec.get('id'), std_heading)

                sheet.set_column(row, col+1, 40)
                sheet.write(row, col + 1, rec.get('emp'), std_heading)

                sheet.set_column(row, col+2, 15)
                sheet.write(row, col + 2, rec.get('date'), std_heading)

                sheet.set_column(row, col + 3, 15)
                sheet.write(row, col + 3, rec.get('desig'), std_heading)

                sheet.set_column(row, col+4, 10)
                sheet.write(row, col + 4, rec.get('worked'), std_heading)

                sheet.set_column(row, col+5, 10)
                sheet.write(row, col + 5, rec.get('absent'), std_heading)

                sheet.set_column(row, col+6, 10)
                sheet.write(row, col + 6, rec.get('Basic Salary'), std_heading)
                sheet.set_column(row, col+7, 10)
                sheet.write(row, col + 7, rec.get('Travel Allowance'), std_heading)
                sheet.set_column(row, col+8, 10)
                sheet.write(row, col + 8, rec.get('Housing Allowance'), std_heading)

                sheet.set_column(row, col+9, 15)
                sheet.write(row, col + 9, rec.get('OT (125) Allowance'), std_heading)
                sheet.set_column(row, col+10, 15)
                sheet.write(row, col + 10, rec.get('OT(1.5) Allowance'), std_heading)
                sheet.set_column(row, col+11, 10)
                sheet.write(row, col + 11, rec.get('ot_tot'), std_heading)

                sheet.set_column(row, col+12, 10)
                sheet.write(row, col + 12, rec.get('Loan Earning'), std_heading)
                sheet.set_column(row, col+13, 15)
                sheet.write(row, col + 13, rec.get('Late In Deduction'), std_heading)
                sheet.set_column(row, col+14, 15)

                sheet.write(row, col + 14, rec.get('Gosi Deduction'), std_heading)
                sheet.set_column(row, col+15, 10)
                sheet.write(row, col + 15, rec.get('Gross'), std_heading)
                sheet.set_column(row, col+16, 10)
                sheet.write(row, col + 16, rec.get('deduc'), std_heading)
                sheet.set_column(row, col+17, 10)

                sheet.write(row, col + 17, rec.get('Net Salary'), std_heading)

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

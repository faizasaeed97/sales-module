# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime
import time
import babel

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_total_paid(self):
        """This compute the total paid amount of Loan."""
        total = 0.0
        if self.state == 'draft':
            for line in self.loan_ids:
                if line.paid:
                    total += line.amount
            self.total_paid = total

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        ttyme = datetime.fromtimestamp(time.mktime(str(time.strptime(date_from), "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
        employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        # computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines

        input_line_ids = self.get_inputs(contract_ids, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines

        total_loan = 0
        if self.employee_id:
            loan_ids = self.env['hr.loan.line'].search([('employee_id', '=', self.employee_id.id), ('paid', '=', False)])
            for loan in loan_ids:
                total_loan = total_loan + loan.amount

        self.has_outstanding = total_loan

        return

    loan_ids = fields.One2many('hr.loan.line', 'payslip_id', string="Loans")
    total_paid = fields.Float(string="Total Loan Amount", compute='compute_total_paid')
    loan_earning = fields.Float(string="Loan To Pay/Paid", help="Loan yet to be Paid by Company")
    has_outstanding = fields.Integer("Has Outstanding Loan")

    def get_loan(self):
        """This gives the installment lines of an employee where the state is not in paid.
            """
        loan_list = []
        dateFrom = datetime.strptime(self.date_from, '%Y-%m-%d')
        loan_ids = self.env['hr.loan.line'].search([('employee_id', '=', self.employee_id.id), ('paid', '=', False)])
        for loan in loan_ids:
            if loan.loan_id:
                loan_d = datetime.strptime(loan.loan_id.loan_date, '%Y-%m-%d')
                if loan.loan_id.appear_payslip:
                    if dateFrom.month == loan_d.month:
                        self.loan_earning = loan.loan_id.loan_amount
                    else:
                        self.loan_earning = 0
                else:
                    self.loan_earning = 0

            if loan.loan_id.state == 'approve':
                loan_list.append(loan.id)
        self.loan_ids = loan_list
        return loan_list

    def action_payslip_done(self):
        loan_list = []
        for line in self.loan_ids:
            if line.paid:
                loan_list.append(line.id)
            else:
                line.payslip_id = False
        self.loan_ids = loan_list
        return super(HrPayslip, self).action_payslip_done()

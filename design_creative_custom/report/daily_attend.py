# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class dailyxtsrdetDetails(models.TransientModel):
    _name = 'daily.attendace.detail'
    _description = "absent Report Details"

    date_d = fields.Date(required=True, string="Date")

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def print_report(self):
        plist = []

        dept = self.env['hr.department'].search(
            [('name','!=','Management')])

        for rec in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = rec.name
            plist.append(dix)

            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            for dec in emps:
                attends = self.env['attendance.custom'].search(
                    [('employee_id', '=', dec.id),
                     ('attendance_date', '=', self.date_d),
                     ])
                if attends:

                    dix = {}
                    dix['roll'] = dec.identification_id

                    dix['emp'] = dec.name
                    dix['dept'] = dec.contract_id.grade.department.name
                    dix['status'] = attends.status
                    dix['title'] = dec.workschedule
                    dix['in'] = attends.first_check_in
                    dix['out'] = attends.first_check_out
                    dix['in2'] = attends.second_check_in
                    dix['out2'] = attends.second_check_out
                    dix['total_hours'] = attends.working

                    dix['ot15'] = attends.ot_15
                    dix['ot125'] = attends.ot_125
                    dix['data'] = 'nd'

                    dix['color'] = "black"

                    if attends.early_in:
                        dix['erly_in'] = "Early In"
                        dix['color'] = "green"


                    elif attends.early_out:
                        dix['erly_in'] = "Early Out"
                        dix['color'] = "green"


                    elif attends.late_in:
                        dix['erly_in'] = "Late in"
                        dix['color'] = "red"

                    plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_from': self.date_d,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.action_report_dailyx_attendance').report_action(self, data=data)


class dailyxtscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.third_attendance'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_f = data['form']['date_from']
        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'df': date_f,
            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

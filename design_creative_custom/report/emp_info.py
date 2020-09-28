# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class logsemprdetDetails(models.TransientModel):
    _name = 'emplog.info.details'
    _description = "Project Report Details"



    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def print_report(self):
        emps = self.env['hr.employee'].search(
            [])
        plist = []
        for rec in emps:
            dix = {}

            dix['emp'] = rec.name
            dix['roll'] = rec.identification_id
            dix['pexp'] = rec.passport_exp_date
            dix['rpexp'] = rec.rp_exp_date
            dix['cprexp'] = rec.cpr_exp_date
            dix['bname'] = rec.bank_name
            dix['bacount'] = rec.bank_account_id.display_name

            plist.append(dix)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {

                'dta': plist

                # 'user_id': self.user_id.id,
                # 'start_date': self.start_date,
                # 'end_date':self.end_date,
                # 'stage_id':self.stage_id.id,
            },
        }
        return self.env.ref('design_creative_custom.action_report_document_empinfox').report_action(self, data=data)


class empinfologscxReport(models.AbstractModel):
    _name = 'report.design_creative_custom.document_report_empinfox'
    _description = "Emp logs Report"

    @api.model
    def _get_report_values(self, docids, data=None):

        datax = data['form']['dta']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],

            'dtax': datax,

            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

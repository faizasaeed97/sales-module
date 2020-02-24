# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectDetails(models.TransientModel):
    _name = 'project.details'
    _description = "Project Report Details"

    project = fields.Many2many('project.project', string='Project', required=True)

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)

    def print_report(self):
        # project_id = self.env.context.get('active_id')
        plist=[]
        for rec in self.project:
            plist.append(rec.id)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'project_id':plist,
                # 'user_id': self.user_id.id,
                # 'start_date': self.start_date,
                # 'end_date':self.end_date,
                # 'stage_id':self.stage_id.id,
            },
        }
        return self.env.ref('project_task_report_app.project_report_action').report_action(self, data=data)

class ProjectTaskReport(models.AbstractModel):
    _name = 'report.project_task_report_app.template_report'
    _description = "Project Report"

    @api.model
    def _get_report_values(self, docids, data=None):

        project_id = data['form']['project_id']
        projects=self.env['project.project'].browse(project_id)
        docs = []
        line=[]

        dpr=[]


        task_amount=0.0
        task_qty=0

        for datas in projects:

            task_ids = self.env['project.task'].search([('project_id','=',datas.id)],order="stage_id desc")

            current_stage = 0
            for task in task_ids:
                if current_stage==task.stage_id.id:
                    current_stage = task.stage_id.id
                    ml=self.env['account.move.line'].search([('project_dc','=',datas.id),('stages','=',current_stage),('tasks','=',task.id)])
                    if ml:
                        for rec in ml:
                            task_amount+=rec.price_total
                            task_qty+=rec.quantity
                        line.append({
                            'name': task.name,
                            'qty': task_qty,
                            'amount': task_amount,
                        })




                else:
                    current_stage = task.stage_id.id
                    ml = self.env['account.move.line'].search(
                        [('project_dc', '=', datas.id), ('stages', '=', current_stage)])
                    if ml:
                        for rec in ml:
                            task_amount += rec.price_total
                            task_qty += rec.quantity
                        auctual=task_amount*task_qty
                        available=task.project_id.amount_count-auctual
                        line.append({'name':task.stage_id.name,'commitment':task.project_id.amount_count,'auctual':auctual,'available':available})
            # line.append(0,{'project':datas.name})
            # docs.append({'project':datas.name})
            dpr.append(datas.name)
            docs.append(line)


            # docs.append({
            #     'name': task.name,
            #     'user_id': task.user_id.name,
            #     'stage': task.stage_id.name,
            #     'planned_hours':task.planned_hours,
            #     'total_hours_spent':task.total_hours_spent,
            #     'remaining_hours':task.remaining_hours,
            #     'date_assign':task.date_assign.date(),
            #     'date_deadline':task.date_deadline,
            # })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
             'dpr':dpr,
            # 'end_date':end_date,
            # 'project_id':self.env['project.project'].browse(project_id),
            # 'stage_id':self.env['project.task.type'].browse(stage_id),
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
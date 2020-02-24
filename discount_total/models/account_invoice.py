from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class AccountInvoice_inh(models.Model):
    _inherit = 'account.move'


    is_commitnment = fields.Boolean(string='Is Commitnment',default=False)





class AccountInvoice_custom(models.Model):
    _inherit = 'account.move.line'

    project_dc = fields.Many2one("project.project", string="Project")
    stages=fields.Many2one(comodel_name="project.task.type", string="Stage")
    tasks=fields.Many2one(comodel_name="project.task", string="task")

    @api.onchange('project')
    def onchange_project(self):
        if self.project.analytic_account_id:
           self.analytic_account_id=self.project.analytic_account_id









class proj_projwork(models.Model):
    _inherit = 'project.project'

    amount_count = fields.Float(Default=0.0,compute="_get_amount")


    def _get_amount(self):
        if self.analytic_account_id:
            getAll=self.env['account.move'].search([('is_commitnment','=',True),('line_ids.analytic_account_id.id','in',[self.analytic_account_id.id])])
            if len(getAll) > 1:
                raise UserError(_('You can only select 1 commitnment ammount in journal items.'))

            amount=0.0
            for rec in getAll:
                for dt in rec.line_ids:
                    amount+=dt.debit

            self.amount_count=amount

    @api.onchange('analytic_account_id')
    def _update_amountx(self):
        if self.analytic_account_id:
            getAll = self.env['account.move'].search([('is_commitnment', '=', True), (
            'line_ids.analytic_account_id.id', 'in', [self.analytic_account_id.id])])
            if len(getAll)>1:
                raise UserError(_('You can only select 1 commitnment ammount in journal items.'))

            amount = 0.0
            for rec in getAll:
                for dt in rec.line_ids:
                    amount += dt.debit

            self.amount_count = amount




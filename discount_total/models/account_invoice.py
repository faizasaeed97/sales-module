from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class AccountInvoice_inh(models.Model):
    _inherit = 'account.move'


    is_commitnment = fields.Boolean(string='Is Commitnment',default=False)





class AccountInvoice_custom(models.Model):
    _inherit = 'account.move.line'

    design_graphice_project = fields.Many2one("project.project", string="Project")
    # stages=fields.Many2one(comodel_name="project.task.type", string="Stage")
    # tasks=fields.Many2one(comodel_name="project.task", string="task")

    # @api.onchange('project')
    # def onchange_project(self):
    #     if self.project.analytic_account_id:
    #        self.analytic_account_id=self.project.analytic_account_id



    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id',
                            move.company_id.currency_id.id)  # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

            if move.is_invoice(include_receipts=True):
                currency = self.env['res.currency'].browse(vals.get('currency_id'))
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.resolve_2many_commands('tax_ids', vals.get('tax_ids', []), fields=['id'])
                tax_ids = set(tax['id'] for tax in taxes)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    if vals.get('currency_id'):
                        balance = vals.get('amount_currency', 0.0)
                    else:
                        balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        balance,
                        move.type,
                        currency,
                        taxes
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.type,
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.type,
                        currency,
                        move.company_id,
                        move.date,
                    ))

            # Ensure consistency between taxes & tax exigibility fields.
            if 'tax_exigible' in vals:
                continue
            if vals.get('tax_repartition_line_id'):
                repartition_line = self.env['account.tax.repartition.line'].browse(vals['tax_repartition_line_id'])
                tax = repartition_line.invoice_tax_id or repartition_line.refund_tax_id
                vals['tax_exigible'] = tax.tax_exigibility == 'on_invoice'
            elif vals.get('tax_ids'):
                tax_ids = [v['id'] for v in self.resolve_2many_commands('tax_ids', vals['tax_ids'], fields=['id'])]
                taxes = self.env['account.tax'].browse(tax_ids).flatten_taxes_hierarchy()
                vals['tax_exigible'] = not any(tax.tax_exigibility == 'on_payment' for tax in taxes)

        if 'project' in vals:
            vals_list['project'] = vals['project']

        lines = super(AccountInvoice_custom, self).create(vals_list)


        moves = lines.mapped('move_id')
        if self._context.get('check_move_validity', True):
            moves._check_balanced()
        moves._check_fiscalyear_lock_date()
        lines._check_tax_lock_date()

        return lines


    # def get_items_proj(self):
    #     val=[]
    #     val['project'] = self.project
    #     val['stages'] = self.stages
    #     val['tasks'] = self.tasks
    #     return val



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




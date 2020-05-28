from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError



class stok_pick_inh(models.Model):
    _inherit='stock.picking'

    def goods_rec_in(self):
        return self.env.ref('cost_sheet_quotations.action_goods_recieved_print').report_action(self)

    def goods_del_out(self):
        return self.env.ref('cost_sheet_quotations.action_goods_return_print').report_action(self)




class acc_pay_inherit(models.Model):
    _inherit='account.payment'


    def payment_rec_out(self):
        return self.env.ref('cost_sheet_quotations.action_payment_voucher_petty_print').report_action(self)

    def payment_rec_in(self):
        return self.env.ref('cost_sheet_quotations.action_customer_payment_print').report_action(self)


    @api.model
    def get_int_val(self):
        amount=self.amount
        int_val= int(amount//1)
        return int_val

    @api.model
    def get_dec_val(self):
        amount=self.amount
        dec_val= (amount%1)
        return dec_val

    def get_journal_line(self):
        active_ids = self.invoice_ids
        final_list = []
        if active_ids:

            invoices = self.env['account.move'].browse(active_ids.ids).filtered(
                lambda move: move.is_invoice(include_receipts=True))
            counter = 0
            for rec in invoices:
                for data in rec.line_ids:
                    counter+=1
                    j_dic = {}
                    j_dic['srn']=counter

                    j_dic['account']=data.account_id.name
                    j_dic['label']=data.name

                    j_dic['debit']=data.debit

                    j_dic['credit']=data.credit
                    final_list.append(j_dic)

        return final_list




class account_projwork(models.Model):
    _inherit = 'account.account'

    def _set_opening_debit_credit(self, amount, field):
        """ Generic function called by both opening_debit and opening_credit's
        inverse function. 'Amount' parameter is the value to be set, and field
        either 'debit' or 'credit', depending on which one of these two fields
        got assigned.
        """
        opening_move = self.company_id.account_opening_move_id

        if not opening_move:
            raise UserError(_("You must first define an opening move."))

        if opening_move.state in ['posted','cancel','draft']:
            # check whether we should create a new move line or modify an existing one
            opening_move_line = self.env['account.move.line'].search([('account_id', '=', self.id),
                                                                      ('move_id','=', opening_move.id),
                                                                      (field,'!=', False),
                                                                      (field,'!=', 0.0)]) # 0.0 condition important for import

            counter_part_map = {'debit': opening_move_line.credit, 'credit': opening_move_line.debit}
            # No typo here! We want the credit value when treating debit and debit value when treating credit

            if opening_move_line:
                if amount:
                    # modify the line
                    opening_move_line.with_context(check_move_validity=False)[field] = amount
                elif counter_part_map[field]:
                    # delete the line (no need to keep a line with value = 0)
                    opening_move_line.with_context(check_move_validity=False).unlink()
            elif amount:
                # create a new line, as none existed before
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': _('Opening balance'),
                        field: amount,
                        'move_id': opening_move.id,
                        'account_id': self.id,
                })

            # Then, we automatically balance the opening move, to make sure it stays valid
            if not 'import_file' in self.env.context:
                # When importing a file, avoid recomputing the opening move for each account and do it at the end, for better performances
                self.company_id._auto_balance_opening_move()




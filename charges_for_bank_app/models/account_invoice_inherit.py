# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date
from datetime import date, timedelta
import ast

from itertools import groupby

class AccountInherit(models.Model):
    _inherit = "account.journal"

    default_bank_account_id = fields.Many2one('account.account', 'Extra Bank Charge Account')

    def open_action(self):
        """return action based on type for related journals"""
        action_name = self._context.get('action_name')

        # Find action based on journal.
        if not action_name:
            if self.type == 'bank':
                action_name = 'action_bank_statement_tree'
            elif self.type == 'cash':
                action_name = 'action_view_bank_statement_tree'
            elif self.type == 'sale':
                action_name = 'action_move_out_invoice_type'
            elif self.type == 'purchase':
                action_name = 'action_move_in_invoice_type'
            else:
                action_name = 'action_bank_statement_tree'

        # Set 'account.' prefix if missing.
        if '.' not in action_name:
            action_name = 'account.%s' % action_name

        action = self.env.ref(action_name).read()[0]
        context = self._context.copy()
        if 'context' in action and type(action['context']) == str:
            context.update(ast.literal_eval(action['context']))
        else:
            context.update(action.get('context', {}))
        action['context'] = context
        action['context'].update({
            'default_journal_id': self.id,
            'search_default_journal_id': self.id,
        })

        domain_type_field = action['res_model'] == 'account.move.line' and 'move_id.type' or 'type' # The model can be either account.move or account.move.line

        if self.type == 'sale':
            action['domain'] = [(domain_type_field, 'in', ('out_invoice', 'out_refund', 'out_receipt'))]
        elif self.type == 'purchase':
            action['domain'] = [(domain_type_field, 'in', ('in_invoice', 'in_refund', 'in_receipt'))]

        return action



class Accountmove_inhrts(models.Model):
    _inherit = "account.move"

    pymnt_ids = fields.Many2one('account.payment', string="paymnt")
    Amount_pay = fields.Float(string="Amount Pay")




class AccountPayment(models.Model):
    _inherit = "account.payment"

    account_payment = fields.Monetary('Extra Bank Charges')
    is_bank_charge = fields.Boolean("Is Bank Charge")
    open_invoices = fields.Many2many('account.move', string="Open Invoices",
                                     )

    @api.onchange('open_invoices', 'open_invoices.Amount_pay')
    def fill_invoices_rec(self):
        if self.partner_id and self.open_invoices:
            amnt = 0.0
            for rec in self.open_invoices:
                if rec.partner_id.id != self.partner_id.id:
                    raise UserError(_("Partner is difffent!"))
                else:
                    amnt += rec.Amount_pay
            self.amount = amnt

    # else:
    # 	raise UserError(_("Please select partner first!"))

    @api.onchange('journal_id')
    def visible_bank_charges(self):
        self.is_bank_charge = False
        if self.journal_id:
            if self.journal_id.type == "bank":
                self.is_bank_charge = True
            else:
                self.is_bank_charge = False

    def post(self):
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids) or any(
                    inv.state != 'posted' for inv in rec.open_invoices):
                raise UserError(_("The payment cannot be processed because the invoice is not open!"))
            if not rec.name:
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            # if rec.journal_id.type == "bank":
                            # 	sequence_code = 'account.payment.customer.invoice.bank'
                            # else:
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            # if rec.journal_id.type == "bank":
                            # 	sequence_code = 'account.payment.customer.refund.bank'
                            # else:
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            # if rec.journal_id.type == "bank":
                            # 	sequence_code = 'account.payment.supplier.refund.bank'
                            # else:
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            # if rec.journal_id.type == "bank":
                            # 	sequence_code = 'account.payment.supplier.invoice.bank'
                            # else:
                            sequence_code = 'account.payment.supplier.invoice'

                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            payment = rec
            if rec.account_payment > 0.0:
                company_currency = rec.company_id.currency_id
                write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
                # Compute amounts.
                write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
                if payment.payment_type in ('outbound', 'transfer'):
                    counterpart_amount = payment.amount
                    liquidity_line_account = payment.journal_id.default_debit_account_id
                else:
                    counterpart_amount = -payment.amount
                    liquidity_line_account = payment.journal_id.default_credit_account_id

                # Manage currency.
                if payment.currency_id == company_currency:
                    # Single-currency.
                    balance = counterpart_amount
                    write_off_balance = write_off_amount
                    counterpart_amount = write_off_amount = 0.0
                    currency_id = False
                else:
                    # Multi-currencies.
                    balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                           payment.payment_date)
                    write_off_balance = payment.currency_id._convert(write_off_amount, company_currency,
                                                                     payment.company_id, payment.payment_date)
                    currency_id = payment.currency_id.id

                # Manage custom currency on journal for liquidity line.
                if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                    liquidity_amount = company_currency._convert(
                        balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    liquidity_amount = counterpart_amount

                if not rec.journal_id.default_bank_account_id:
                    raise UserError(
                        'Please first configure  [Bank Charge Account] from Invoicing Configuration -> Journals -> Bank(Extra Bank Charge Account)..!')

                debit = (0, 0, {'name': "Bank Charge :" + str(rec.communication),
                                'amount_currency': counterpart_amount + write_off_amount,
                                'currency_id': currency_id,
                                'debit': rec.account_payment,
                                'credit': 0.0,
                                'date_maturity': rec.payment_date,
                                'partner_id': rec.partner_id.id,
                                'account_id': rec.journal_id.default_bank_account_id.id,
                                'rec': rec.id,
                                'journal_id': rec.journal_id.id,
                                })

                amount_currency = 0.0
                if rec.payment_type == 'outbound':
                    amount_currency = -liquidity_amount
                if rec.payment_type == 'inbound':
                    amount_currency = liquidity_amount

                credit = (0, 0, {'name': rec.name,
                                 'amount_currency': amount_currency,
                                 'currency_id': liquidity_line_currency_id,
                                 'debit': 0.0,
                                 'credit': rec.account_payment,
                                 'date_maturity': rec.payment_date,
                                 'partner_id': rec.partner_id.id,
                                 'account_id': rec.journal_id.default_credit_account_id.id,
                                 'payment_id': rec.id,
                                 'journal_id': rec.journal_id.id})

                debit = (0, 0, {'name': "Bank Charge :" + str(rec.communication),
                                'amount_currency': liquidity_amount,
                                'currency_id': currency_id,
                                'debit': rec.account_payment,
                                'credit': 0.0,
                                'date_maturity': rec.payment_date,
                                'partner_id': rec.partner_id.id,
                                'account_id': rec.journal_id.default_bank_account_id.id,
                                'payment_id': rec.id,
                                'journal_id': rec.journal_id.id,
                                })

                move_line_data = rec._prepare_payment_moves()
            # move_line_data[0]['line_ids'].append(debit)
            # move_line_data[0]['line_ids'].append(credit)

            if len(rec.open_invoices) > 0:
                company_currency = rec.company_id.currency_id
                write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
                # Compute amounts.
                write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
                if payment.payment_type in ('outbound', 'transfer'):
                    counterpart_amount = payment.amount
                    liquidity_line_account = payment.journal_id.default_debit_account_id
                else:
                    counterpart_amount = -payment.amount
                    liquidity_line_account = payment.journal_id.default_credit_account_id

                # Manage currency.
                if payment.currency_id == company_currency:
                    # Single-currency.
                    balance = counterpart_amount
                    write_off_balance = write_off_amount
                    counterpart_amount = write_off_amount = 0.0
                    currency_id = False
                else:
                    # Multi-currencies.
                    balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
                                                           payment.payment_date)
                    write_off_balance = payment.currency_id._convert(write_off_amount, company_currency,
                                                                     payment.company_id, payment.payment_date)
                    currency_id = payment.currency_id.id

                # Manage custom currency on journal for liquidity line.
                if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                    liquidity_amount = company_currency._convert(
                        balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    liquidity_amount = counterpart_amount

                # if not rec.journal_id.default_bank_account_id:
                # 	raise UserError('Please first configure  [Bank Charge Account] from Invoicing Configuration -> Journals -> Bank(Extra Bank Charge Account)..!')
                move_line_data = rec._prepare_payment_moves()

                for recor in rec.open_invoices:

                    debit = (0, 0, {'name': "multi invoice par-pay :" + str(rec.communication),
                                    'amount_currency': recor.Amount_pay,
                                    'currency_id': currency_id,
                                    'debit': recor.Amount_pay,
                                    'credit': 0.0,
                                    'date_maturity': rec.payment_date,
                                    'partner_id': rec.partner_id.id,
                                    'account_id': payment.destination_account_id.id,
                                    'payment_id': rec.id,
                                    'journal_id': rec.journal_id.id,
                                    })

                    amount_currency = 0.0
                    if rec.payment_type == 'outbound':
                        amount_currency = -recor.Amount_pay
                    if rec.payment_type == 'inbound':
                        amount_currency = recor.Amount_pay

                    credit = (0, 0, {'name': rec.name,
                                     'amount_currency': amount_currency,
                                     'currency_id': liquidity_line_currency_id,
                                     'debit': 0.0,
                                     'credit': recor.Amount_pay,
                                     'date_maturity': rec.payment_date,
                                     'partner_id': rec.partner_id.id,
                                     'account_id': rec.journal_id.default_credit_account_id.id,
                                     'payment_id': rec.id,
                                     'journal_id': rec.journal_id.id})

                    # debit = (0, 0, {'name': "Bank Charge :"+str(rec.communication),
                    #   'amount_currency': liquidity_amount,
                    #   'currency_id': currency_id,
                    #   'debit': rec.account_payment,
                    #   'credit': 0.0,
                    #   'date_maturity': rec.payment_date,
                    #   'partner_id': rec.partner_id.id,
                    #   'account_id': rec.journal_id.default_bank_account_id.id,
                    #   'payment_id': rec.id,
                    #   'journal_id':rec.journal_id.id,
                    #   })

                    move_line_data[0]['line_ids'].append(debit)
                    move_line_data[0]['line_ids'].append(credit)


            else:
                move_line_data = rec._prepare_payment_moves()

            moves = AccountMove.create(move_line_data)
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (moves[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id) \
                        .reconcile()
                if rec.open_invoices:
                    (moves[0] + rec.open_invoices).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id) \
                        .reconcile()

            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                moves.mapped('line_ids') \
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id) \
                    .reconcile()

        return True


# class payment_register_inherit(models.TransientModel):
#     _inherit = 'account.payment.register'
#
#     invoice_ids = fields.Many2many('account.move', 'account_invoice_payment_rel_transient', 'payment_id', 'invoice_id',
#                                    string="Invoices", copy=False, readonly=False)
#     Amount_pay = fields.Float(string="Amount Pay")
#
#     @api.onchange('invoice_ids', 'invoice_ids.Amount_pay')
#     def fill_invoices_rec(self):
#         if self.partner_id and self.invoice_ids:
#             amnt = 0.0
#             for rec in self.invoice_ids:
#                 if rec.partner_id.id != self.partner_id.id:
#                     raise UserError(_("Partner is difffent!"))
#                 else:
#                     amnt += rec.Amount_pay
#             self.amount = amnt


class AccountReconcileModelinh(models.TransientModel):
    _inherit = 'account.payment.register'

    invoice_ids = fields.Many2many('account.move', 'account_invoice_payment_rel_transient', 'payment_id', 'invoice_id',
                                   string="Invoices", copy=False, readonly=False)
    Amount_pay = fields.Float(string="Amount Pay")

    @api.onchange('invoice_ids', 'invoice_ids.Amount_pay')
    def fill_invoices_rec(self):
        if self.invoice_ids:
            amnt = 0.0
            for rec in self.invoice_ids:
                amnt += rec.Amount_pay
            self.Amount_pay = amnt

    # def _prepare_payment_vals(self, invoices):
    #     '''Create the payment values.
    #
    #     :param invoices: The invoices/bills to pay. In case of multiple
    #         documents, they need to be grouped by partner, bank, journal and
    #         currency.
    #     :return: The payment values as a dictionary.
    #     '''
    #     amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
    #     # for rec in invoices:
    #     #     self.tot_amount+=rec.Amount_pay
    #     #
    #     # amount = self.Amount_pay
    #
    #     values = {
    #         'journal_id': self.journal_id.id,
    #         'payment_method_id': self.payment_method_id.id,
    #         'payment_date': self.payment_date,
    #         'communication': " ".join(i.ref or i.name for i in invoices),
    #         'invoice_ids': [(6, 0, invoices.ids)],
    #         'payment_type': ('inbound' if amount > 0 else 'outbound'),
    #         'amount': abs(amount),
    #         'currency_id': invoices[0].currency_id.id,
    #         'partner_id': invoices[0].commercial_partner_id.id,
    #         'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
    #         'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
    #     }
    #     return values
    #
    # def get_payments_vals(self):
    #     '''Compute the values for payments.
    #
    #     :return: a list of payment values (dictionary).
    #     '''
    #     grouped = defaultdict(lambda: self.env["account.move"])
    #     for inv in self.invoice_ids:
    #         if self.group_payment:
    #             grouped[(inv.commercial_partner_id, inv.currency_id, inv.invoice_partner_bank_id, MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type])] += inv
    #         else:
    #             grouped[inv.id] += inv
    #     return [self._prepare_payment_vals(invoices) for invoices in grouped.values()]
    #
    # def create_payments(self):
    #     '''Create payments according to the invoices.
    #     Having invoices with different commercial_partner_id or different type
    #     (Vendor bills with customer invoices) leads to multiple payments.
    #     In case of all the invoices are related to the same
    #     commercial_partner_id and have the same type, only one payment will be
    #     created.
    #
    #     :return: The ir.actions.act_window to show created payments.
    #     '''
    #     Payment = self.env['account.payment']
    #     payments = Payment.create(self.get_payments_vals())
    #     payments.post()
    #
    #     action_vals = {
    #         'name': _('Payments'),
    #         'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
    #         'res_model': 'account.payment',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #     }
    #     if len(payments) == 1:
    #         action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
    #     else:
    #         action_vals['view_mode'] = 'tree,form'
    #     return action_vals

class AccountReconcileamlModelinh(models.Model):
    _inherit = 'account.move.line'



    def check_full_reconcile(self):
        """
        This method check if a move is totally reconciled and if we need to create exchange rate entries for the move.
        In case exchange rate entries needs to be created, one will be created per currency present.
        In case of full reconciliation, all moves belonging to the reconciliation will belong to the same account_full_reconcile object.
        """
        # Get first all aml involved
        todo = self.env['account.partial.reconcile'].search_read(['|', ('debit_move_id', 'in', self.ids), ('credit_move_id', 'in', self.ids)], ['debit_move_id', 'credit_move_id'])
        amls = set(self.ids)
        seen = set()
        while todo:
            aml_ids = [rec['debit_move_id'][0] for rec in todo if rec['debit_move_id']] + [rec['credit_move_id'][0] for rec in todo if rec['credit_move_id']]
            amls |= set(aml_ids)
            seen |= set([rec['id'] for rec in todo])
            todo = self.env['account.partial.reconcile'].search_read(['&', '|', ('credit_move_id', 'in', aml_ids), ('debit_move_id', 'in', aml_ids), '!', ('id', 'in', list(seen))], ['debit_move_id', 'credit_move_id'])

        partial_rec_ids = list(seen)
        if not amls:
            return
        else:
            amls = self.browse(list(amls))

        # If we have multiple currency, we can only base ourselves on debit-credit to see if it is fully reconciled
        currency = set([a.currency_id for a in amls if a.currency_id.id != False])
        multiple_currency = False
        if len(currency) != 1:
            currency = False
            multiple_currency = True
        else:
            currency = list(currency)[0]
        # Get the sum(debit, credit, amount_currency) of all amls involved
        total_debit = 0
        total_credit = 0
        total_amount_currency = 0
        maxdate = date.min
        to_balance = {}
        cash_basis_partial = self.env['account.partial.reconcile']
        for aml in amls:
            cash_basis_partial |= aml.move_id.tax_cash_basis_rec_id
            total_debit += aml.debit
            total_credit += aml.credit
            maxdate = max(aml.date, maxdate)
            total_amount_currency += aml.amount_currency
            # Convert in currency if we only have one currency and no amount_currency
            if not aml.amount_currency and currency:
                multiple_currency = True
                total_amount_currency += aml.company_id.currency_id._convert(aml.balance, currency, aml.company_id, aml.date)
            # If we still have residual value, it means that this move might need to be balanced using an exchange rate entry
            if aml.amount_residual != 0 or aml.amount_residual_currency != 0:
                if not to_balance.get(aml.currency_id):
                    to_balance[aml.currency_id] = [self.env['account.move.line'], 0]
                to_balance[aml.currency_id][0] += aml
                to_balance[aml.currency_id][1] += aml.amount_residual != 0 and aml.amount_residual or aml.amount_residual_currency

        # Check if reconciliation is total
        # To check if reconciliation is total we have 3 different use case:
        # 1) There are multiple currency different than company currency, in that case we check using debit-credit
        # 2) We only have one currency which is different than company currency, in that case we check using amount_currency
        # 3) We have only one currency and some entries that don't have a secundary currency, in that case we check debit-credit
        #   or amount_currency.
        # 4) Cash basis full reconciliation
        #     - either none of the moves are cash basis reconciled, and we proceed
        #     - or some moves are cash basis reconciled and we make sure they are all fully reconciled

        digits_rounding_precision = amls[0].company_id.currency_id.rounding
        if (
                (
                    not cash_basis_partial or (cash_basis_partial and all([p >= 1.0 for p in amls._get_matched_percentage().values()]))
                ) and
                (
                    currency and float_is_zero(total_amount_currency, precision_rounding=currency.rounding) or
                    multiple_currency and float_compare(total_debit, total_credit, precision_rounding=digits_rounding_precision) == 0
                )
        ):

            exchange_move_id = False
            missing_exchange_difference = False
            # Eventually create a journal entry to book the difference due to foreign currency's exchange rate that fluctuates
            if to_balance and any([not float_is_zero(residual, precision_rounding=digits_rounding_precision) for aml, residual in to_balance.values()]):
                if not self.env.context.get('no_exchange_difference'):
                    exchange_move = self.env['account.move'].with_context(default_type='entry').create(
                        self.env['account.full.reconcile']._prepare_exchange_diff_move(move_date=maxdate, company=amls[0].company_id))
                    part_reconcile = self.env['account.partial.reconcile']
                    for aml_to_balance, total in to_balance.values():
                        if total:
                            rate_diff_amls, rate_diff_partial_rec = part_reconcile.create_exchange_rate_entry(aml_to_balance, exchange_move)
                            amls += rate_diff_amls
                            partial_rec_ids += rate_diff_partial_rec.ids
                        else:
                            aml_to_balance.reconcile()
                    exchange_move.post()
                    exchange_move_id = exchange_move.id
                else:
                    missing_exchange_difference = True
            if not missing_exchange_difference:
                #mark the reference of the full reconciliation on the exchange rate entries and on the entries
                self.env['account.full.reconcile'].create({
                    'partial_reconcile_ids': [(6, 0, partial_rec_ids)],
                    'reconciled_line_ids': [(6, 0, amls.ids)],
                    'exchange_move_id': exchange_move_id,
                })

    def _reconcile_lines(self, debit_moves, credit_moves, field):
        """ This function loops on the 2 recordsets given as parameter as long as it
            can find a debit and a credit to reconcile together. It returns the recordset of the
            account move lines that were not reconciled during the process.
        """

        (debit_moves + credit_moves).read([field])
        to_create = []
        cash_basis = debit_moves and debit_moves[0].account_id.internal_type in ('receivable', 'payable') or False
        cash_basis_percentage_before_rec = {}
        dc_vals ={}
        while (debit_moves and credit_moves):
            debit_move = debit_moves[0]
            credit_move = credit_moves[0]
            company_currency = debit_move.company_id.currency_id
            # We need those temporary value otherwise the computation might be wrong below
            temp_amount_residual = min(debit_move.amount_residual, -credit_move.amount_residual)
            temp_amount_residual_currency = min(debit_move.amount_residual_currency, -credit_move.amount_residual_currency)
            dc_vals[(debit_move.id, credit_move.id)] = (debit_move, credit_move, temp_amount_residual_currency)
            amount_reconcile = min(debit_move[field], -credit_move[field])

            #Remove from recordset the one(s) that will be totally reconciled
            # For optimization purpose, the creation of the partial_reconcile are done at the end,
            # therefore during the process of reconciling several move lines, there are actually no recompute performed by the orm
            # and thus the amount_residual are not recomputed, hence we have to do it manually.
            if amount_reconcile == debit_move[field]:
                debit_moves -= debit_move
            else:
                debit_moves[0].amount_residual -= temp_amount_residual
                debit_moves[0].amount_residual_currency -= temp_amount_residual_currency

            if amount_reconcile == -credit_move[field]:
                credit_moves -= credit_move
            else:
                credit_moves[0].amount_residual += temp_amount_residual
                credit_moves[0].amount_residual_currency += temp_amount_residual_currency
            #Check for the currency and amount_currency we can set
            currency = False
            amount_reconcile_currency = 0
            if field == 'amount_residual_currency':
                currency = credit_move.currency_id.id
                amount_reconcile_currency = temp_amount_residual_currency
                amount_reconcile = temp_amount_residual

            if cash_basis:
                tmp_set = debit_move | credit_move
                cash_basis_percentage_before_rec.update(tmp_set._get_matched_percentage())

            to_create.append({
                'debit_move_id': debit_move.id,
                'credit_move_id': credit_move.id,
                'amount': amount_reconcile,
                'amount_currency': amount_reconcile_currency,
                'currency_id': currency,
            })

        cash_basis_subjected = []
        part_rec = self.env['account.partial.reconcile']
        for partial_rec_dict in to_create:
            debit_move, credit_move, amount_residual_currency = dc_vals[partial_rec_dict['debit_move_id'], partial_rec_dict['credit_move_id']]
            # /!\ NOTE: Exchange rate differences shouldn't create cash basis entries
            # i. e: we don't really receive/give money in a customer/provider fashion
            # Since those are not subjected to cash basis computation we process them first
            if not amount_residual_currency and debit_move.currency_id and credit_move.currency_id:
                part_rec.create(partial_rec_dict)
            else:
                cash_basis_subjected.append(partial_rec_dict)

        for after_rec_dict in cash_basis_subjected:
            new_rec = part_rec.create(after_rec_dict)
            # if the pair belongs to move being reverted, do not create CABA entry
            if cash_basis and not (
                    new_rec.debit_move_id.move_id == new_rec.credit_move_id.move_id.reversed_entry_id
                    or
                    new_rec.credit_move_id.move_id == new_rec.debit_move_id.move_id.reversed_entry_id
            ):
                new_rec.create_tax_cash_basis_entry(cash_basis_percentage_before_rec)
        return debit_moves+credit_moves

    def auto_reconcile_lines(self):
        # Create list of debit and list of credit move ordered by date-currency
        debit_moves = self.filtered(lambda r: r.debit != 0 or r.amount_currency > 0)
        credit_moves = self.filtered(lambda r: r.credit != 0 or r.amount_currency < 0)
        debit_moves = debit_moves.sorted(key=lambda a: (a.date_maturity or a.date, a.currency_id))
        credit_moves = credit_moves.sorted(key=lambda a: (a.date_maturity or a.date, a.currency_id))
        # Compute on which field reconciliation should be based upon:
        if self[0].account_id.currency_id and self[0].account_id.currency_id != self[0].account_id.company_id.currency_id:
            field = 'amount_residual_currency'
        else:
            field = 'amount_residual'
        #if all lines share the same currency, use amount_residual_currency to avoid currency rounding error
        if self[0].currency_id and all([x.amount_currency and x.currency_id == self[0].currency_id for x in self]):
            field = 'amount_residual_currency'
        # Reconcile lines
        ret = self._reconcile_lines(debit_moves, credit_moves, field)
        return ret

    def _check_reconcile_validity(self):
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries.'))
        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (all_accounts[0].name, all_accounts[0].code))

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Empty self can happen if the user tries to reconcile entries which are already reconciled.
        # The calling method might have filtered out reconciled lines.
        if not self:
            return

        self._check_reconcile_validity()
        #reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        writeoff_to_reconcile = self.env['account.move.line']
        #if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff([writeoff_vals])
            #add writeoff line to reconcile algorithm and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
        # Check if reconciliation is total or needs an exchange rate entry to be created
        (self + writeoff_to_reconcile).check_full_reconcile()
        return True

    def _create_writeoff(self, writeoff_vals):
        """ Create a writeoff move per journal for the account.move.lines in self. If debit/credit is not specified in vals,
            the writeoff amount will be computed as the sum of amount_residual of the given recordset.
            :param writeoff_vals: list of dicts containing values suitable for account_move_line.create(). The data in vals will
                be processed to create bot writeoff account.move.line and their enclosing account.move.
        """
        def compute_writeoff_counterpart_vals(values):
            line_values = values.copy()
            line_values['debit'], line_values['credit'] = line_values['credit'], line_values['debit']
            if 'amount_currency' in values:
                line_values['amount_currency'] = -line_values['amount_currency']
            return line_values
        # Group writeoff_vals by journals
        writeoff_dict = {}
        for val in writeoff_vals:
            journal_id = val.get('journal_id', False)
            if not writeoff_dict.get(journal_id, False):
                writeoff_dict[journal_id] = [val]
            else:
                writeoff_dict[journal_id].append(val)

        partner_id = self.env['res.partner']._find_accounting_partner(self[0].partner_id).id
        company_currency = self[0].account_id.company_id.currency_id
        writeoff_currency = self[0].account_id.currency_id or company_currency
        line_to_reconcile = self.env['account.move.line']
        # Iterate and create one writeoff by journal
        writeoff_moves = self.env['account.move']
        for journal_id, lines in writeoff_dict.items():
            total = 0
            total_currency = 0
            writeoff_lines = []
            date = fields.Date.today()
            for vals in lines:
                # Check and complete vals
                if 'account_id' not in vals or 'journal_id' not in vals:
                    raise UserError(_("It is mandatory to specify an account and a journal to create a write-off."))
                if ('debit' in vals) ^ ('credit' in vals):
                    raise UserError(_("Either pass both debit and credit or none."))
                if 'date' not in vals:
                    vals['date'] = self._context.get('date_p') or fields.Date.today()
                vals['date'] = fields.Date.to_date(vals['date'])
                if vals['date'] and vals['date'] < date:
                    date = vals['date']
                if 'name' not in vals:
                    vals['name'] = self._context.get('comment') or _('Write-Off')
                if 'analytic_account_id' not in vals:
                    vals['analytic_account_id'] = self.env.context.get('analytic_id', False)
                #compute the writeoff amount if not given
                if 'credit' not in vals and 'debit' not in vals:
                    amount = sum([r.amount_residual for r in self])
                    vals['credit'] = amount > 0 and amount or 0.0
                    vals['debit'] = amount < 0 and abs(amount) or 0.0
                vals['partner_id'] = partner_id
                total += vals['debit']-vals['credit']
                if 'amount_currency' not in vals and writeoff_currency != company_currency:
                    vals['currency_id'] = writeoff_currency.id
                    sign = 1 if vals['debit'] > 0 else -1
                    vals['amount_currency'] = sign * abs(sum([r.amount_residual_currency for r in self]))
                    total_currency += vals['amount_currency']

                writeoff_lines.append(compute_writeoff_counterpart_vals(vals))

            # Create balance line
            writeoff_lines.append({
                'name': _('Write-Off'),
                'debit': total > 0 and total or 0.0,
                'credit': total < 0 and -total or 0.0,
                'amount_currency': total_currency,
                'currency_id': total_currency and writeoff_currency.id or False,
                'journal_id': journal_id,
                'account_id': self[0].account_id.id,
                'partner_id': partner_id
                })

            # Create the move
            writeoff_move = self.env['account.move'].create({
                'journal_id': journal_id,
                'date': date,
                'state': 'draft',
                'line_ids': [(0, 0, line) for line in writeoff_lines],
            })
            writeoff_moves += writeoff_move
            line_to_reconcile += writeoff_move.line_ids.filtered(lambda r: r.account_id == self[0].account_id).sorted(key='id')[-1:]

        #post all the writeoff moves at once
        if writeoff_moves:
            writeoff_moves.post()

        # Return the writeoff move.line which is to be reconciled
        return line_to_reconcile

# class AccountReconciliation(models.AbstractModel):
#     _inherit = 'account.reconciliation.widget'
#
#     ####################################################
#     # Public
#     ####################################################
#
#     @api.model
#     def get_move_lines_by_batch_payment(self, st_line_id, batch_payment_id):
#         """ As get_move_lines_for_bank_statement_line, but returns lines from a batch deposit """
#         st_line = self.env['account.bank.statement.line'].browse(st_line_id)
#         move_lines = self.env['account.move.line']
#         # batch deposits from any journal can be selected in bank statement reconciliation widget,
#         # so we need to filter not only on lines of type 'liquidity' but also on any bank/cash
#         # account set as 'Allow Reconciliation'.
#         move_lines = self.env['account.move.line']
#         for payment in self.env['account.batch.payment'].browse(batch_payment_id).payment_ids:
#             journal_accounts = [payment.journal_id.default_debit_account_id.id, payment.journal_id.default_credit_account_id.id]
#             move_lines |= payment.move_line_ids.filtered(lambda r: r.account_id.id in journal_accounts)
#
#         target_currency = st_line.currency_id or st_line.journal_id.currency_id or st_line.journal_id.company_id.currency_id
#         return self._prepare_move_lines(move_lines, target_currency=target_currency, target_date=st_line.date)
#
#     @api.model
#     def get_batch_payments_data(self, bank_statement_ids):
#         """ Return a list of dicts containing informations about unreconciled batch deposits """
#
#         Batch_payment = self.env['account.batch.payment']
#
#         batch_payments = []
#         batch_payments_domain = [('state', '!=', 'reconciled')]
#         for batch_payment in Batch_payment.search(batch_payments_domain, order='id asc'):
#             payments = batch_payment.payment_ids
#             journal = batch_payment.journal_id
#             company_currency = journal.company_id.currency_id
#             journal_currency = journal.currency_id or company_currency
#
#             amount_journal_currency = formatLang(self.env, batch_payment.amount, currency_obj=journal_currency)
#             amount_payment_currency = False
#             # If all the payments of the deposit are in another currency than the journal currency, we'll display amount in both currencies
#             if payments and all(p.currency_id != journal_currency and p.currency_id == payments[0].currency_id for p in payments):
#                 amount_payment_currency = sum(p.amount for p in payments)
#                 amount_payment_currency = formatLang(self.env, amount_payment_currency, currency_obj=payments[0].currency_id or company_currency)
#
#             batch_payments.append({
#                 'id': batch_payment.id,
#                 'name': batch_payment.name,
#                 'date': format_date(self.env, batch_payment.date),
#                 'journal_id': journal.id,
#                 'amount_str': amount_journal_currency,
#                 'amount_currency_str': amount_payment_currency,
#             })
#         return batch_payments

class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    def _compute_number_entries(self):
        data = self.env['account.move.line'].read_group([('reconcile_model_id', 'in', self.ids)], ['reconcile_model_id'], 'reconcile_model_id')
        mapped_data = dict([(d['reconcile_model_id'][0], d['reconcile_model_id_count']) for d in data])
        for model in self:
            model.number_entries = mapped_data.get(model.id, 0)

class bankstmantinherit(models.Model):
    _inherit = 'account.bank.statement'


    cheque_no=fields.Char(string="Cheque No",)
    chq_date=fields.Date(string="Cheque Date")
    purpose= fields.Char(string="Purpose")

    payee_name = fields.Char("Payee Name")


    def action_bank_reconcile_bank_statements(self):
        self.ensure_one()
        bank_stmt_lines = self.mapped('line_ids')
        return {
            'type': 'ir.actions.client',
            'tag': 'bank_statement_reconciliation_view',
            'context': {'statement_line_ids': bank_stmt_lines.ids, 'company_ids': self.mapped('company_id').ids},
        }


    def fast_counterpart_creation(self):
        """This function is called when confirming a bank statement and will allow to automatically process lines without
        going in the bank reconciliation widget. By setting an account_id on bank statement lines, it will create a journal
        entry using that account to counterpart the bank account
        """
        payment_list = []
        move_list = []
        account_type_receivable = self.env.ref('account.data_account_type_receivable')
        already_done_stmt_line_ids = [a['statement_line_id'][0] for a in self.env['account.move.line'].read_group([('statement_line_id', 'in', self.ids)], ['statement_line_id'], ['statement_line_id'])]
        managed_st_line = []
        for st_line in self:
            # Technical functionality to automatically reconcile by creating a new move line
            if st_line.account_id and not st_line.id in already_done_stmt_line_ids:
                managed_st_line.append(st_line.id)
                # Create payment vals
                total = st_line.amount
                payment_methods = (total > 0) and st_line.journal_id.inbound_payment_method_ids or st_line.journal_id.outbound_payment_method_ids
                currency = st_line.journal_id.currency_id or st_line.company_id.currency_id
                partner_type = 'customer' if st_line.account_id.user_type_id == account_type_receivable else 'supplier'
                payment_list.append({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': total > 0 and 'inbound' or 'outbound',
                    'partner_id': st_line.partner_id.id,
                    'partner_type': partner_type,
                    'journal_id': st_line.statement_id.journal_id.id,
                    'payment_date': st_line.date,
                    'state': 'reconciled',
                    'currency_id': currency.id,
                    'amount': abs(total),
                    'communication': st_line._get_communication(payment_methods[0] if payment_methods else False),
                    'name': st_line.statement_id.name or _("Bank Statement %s") % st_line.date,
                })

                # Create move and move line vals
                move_vals = st_line._prepare_reconciliation_move(st_line.statement_id.name)
                aml_dict = {
                    'name': st_line.name,
                    'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                    'credit': st_line.amount > 0 and st_line.amount or 0.0,
                    'account_id': st_line.account_id.id,
                    'partner_id': st_line.partner_id.id,
                    'statement_line_id': st_line.id,
                }
                st_line._prepare_move_line_for_currency(aml_dict, st_line.date or fields.Date.context_today())
                move_vals['line_ids'] = [(0, 0, aml_dict)]
                balance_line = self._prepare_reconciliation_move_line(
                    move_vals, -aml_dict['debit'] if st_line.amount < 0 else aml_dict['credit'])
                move_vals['line_ids'].append((0, 0, balance_line))
                move_list.append(move_vals)

        # Creates
        payment_ids = self.env['account.payment'].create(payment_list)
        for payment_id, move_vals in zip(payment_ids, move_list):
            for line in move_vals['line_ids']:
                line[2]['payment_id'] = payment_id.id
        move_ids = self.env['account.move'].create(move_list)
        move_ids.post()

        for move, st_line, payment in zip(move_ids, self.browse(managed_st_line), payment_ids):
            st_line.write({'move_name': move.name})
            payment.write({'payment_reference': move.name})

#
#     @api.model
#     def get_bank_statement_data(self, bank_statement_line_ids, srch_domain=[]):
#         """ Add batch payments data to the dict returned """
#         res = super(AccountReconciliation, self).get_bank_statement_data(bank_statement_line_ids, srch_domain)
#         res.update({'batch_payments': self.get_batch_payments_data(bank_statement_line_ids)})
#         return res

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"




    def _prepare_payment_vals(self, total):
        """ Prepare the dict of values to create the payment from a statement line. This method may be overridden for update dict
            through model inheritance (make sure to call super() to establish a clean extension chain).

           :param float total: will be used as the amount of the generated payment
           :return: dict of value to create() the account.payment
        """
        self.ensure_one()
        partner_type = False
        if self.partner_id:
            if total < 0:
                partner_type = 'supplier'
            else:
                partner_type = 'customer'
        if not partner_type and self.env.context.get('default_partner_type'):
            partner_type = self.env.context['default_partner_type']
        currency = self.journal_id.currency_id or self.company_id.currency_id
        payment_methods = (total > 0) and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
        return {
            'payment_method_id': payment_methods and payment_methods[0].id or False,
            'payment_type': total > 0 and 'inbound' or 'outbound',
            'partner_id': self.partner_id.id,
            'partner_type': partner_type,
            'journal_id': self.statement_id.journal_id.id,
            'payment_date': self.date,
            'state': 'reconciled',
            'cheque_no': self.statement_id.cheque_no,

            'chq_date': self.statement_id.chq_date,
            'purpose': self.statement_id.purpose,
            'payee_name': self.statement_id.payee_name,
            'currency_id': currency.id,
            'amount': abs(total),
            'communication': self._get_communication(payment_methods[0] if payment_methods else False),
            'name': self.statement_id.name or _("Bank Statement %s") %  self.date,
        }


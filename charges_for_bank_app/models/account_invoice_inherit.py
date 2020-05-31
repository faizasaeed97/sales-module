# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInherit(models.Model):
	_inherit = "account.journal"

	default_bank_account_id = fields.Many2one('account.account', 'Extra Bank Charge Account')


class AccountPayment(models.Model):
	_inherit = "account.payment"


	account_payment = fields.Monetary('Extra Bank Charges')
	is_bank_charge = fields.Boolean("Is Bank Charge")


	@api.onchange('journal_id')
	def visible_bank_charges(self):
		self.is_bank_charge = False
		if self.journal_id:
			if self.journal_id.name == "Bank":
				self.is_bank_charge = True
			else:
				self.is_bank_charge = False

	def post(self):

		AccountMove = self.env['account.move'].with_context(default_type='entry')
		for rec in self:

			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted."))

			if any(inv.state != 'posted' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
			if not rec.name:
				if rec.payment_type == 'transfer':
					sequence_code = 'account.payment.transfer'
				else:
					if rec.partner_type == 'customer':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.customer.invoice'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.customer.refund'
					if rec.partner_type == 'supplier':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.supplier.refund'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.supplier.invoice'
				rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
				if not rec.name and rec.payment_type != 'transfer':
					raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))


			payment = rec
			if  rec.account_payment > 0.0:
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
					balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
					write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
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
					raise UserError('Please first configure  [Bank Charge Account] from Invoicing Configuration -> Journals -> Bank(Extra Bank Charge Account)..!')

				debit = (0, 0, {'name': "Bank Charge :"+str(rec.communication),
				  'amount_currency': counterpart_amount + write_off_amount,
				  'currency_id': currency_id,
				  'debit': rec.account_payment,
				  'credit': 0.0,
				  'date_maturity': rec.payment_date,
				  'partner_id': rec.partner_id.id,
				  'account_id': rec.journal_id.default_bank_account_id.id,
				  'rec': rec.id,
				  'journal_id':rec.journal_id.id,
				  })

				amount_currency = 0.0
				if rec.payment_type == 'outbound':
					amount_currency = -liquidity_amount
				if rec.payment_type == 'inbound':
					amount_currency = liquidity_amount

				credit =(0, 0, {'name': rec.name,
				  'amount_currency': amount_currency,
				  'currency_id': liquidity_line_currency_id,
				  'debit': 0.0,
				  'credit': rec.account_payment,
				  'date_maturity': rec.payment_date,
				  'partner_id': rec.partner_id.id,
				  'account_id': rec.journal_id.default_credit_account_id.id,
				  'payment_id': rec.id,
				  'journal_id':rec.journal_id.id})

				debit = (0, 0, {'name': "Bank Charge :"+str(rec.communication),
				  'amount_currency': liquidity_amount,
				  'currency_id': currency_id,
				  'debit': rec.account_payment,
				  'credit': 0.0,
				  'date_maturity': rec.payment_date,
				  'partner_id': rec.partner_id.id,
				  'account_id': rec.journal_id.default_bank_account_id.id,
				  'payment_id': rec.id,
				  'journal_id':rec.journal_id.id,
				  })

				move_line_data = rec._prepare_payment_moves()
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
						.filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id)\
						.reconcile()
			elif rec.payment_type == 'transfer':
				# ==== 'transfer' ====
				moves.mapped('line_ids')\
					.filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
					.reconcile()

		return True
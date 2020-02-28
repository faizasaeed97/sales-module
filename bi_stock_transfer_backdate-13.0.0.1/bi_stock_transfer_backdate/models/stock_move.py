# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from  datetime import datetime
from odoo.exceptions import UserError,Warning 


class StockMoveUpdate(models.Model):
    _inherit = 'stock.move'

    remark = fields.Char(String="Remarks", copy=False)
    transfer_date = fields.Datetime(String="Transfer Date", copy=False)

    def _action_done(self,cancel_backorder=False):
        res = super(StockMoveUpdate, self)._action_done()
        custom_stock_picking_ids = self.env['stock.picking'].browse(self._context.get('active_id'))
        stock_type_id = self.env['stock.picking.type'].browse(self._context.get('active_id'))
        if custom_stock_picking_ids.picking_type_id.code in ('outgoing'):
            for move in res:
                move.write({'date': move.transfer_date or fields.Datetime.now()})
                for line in move.mapped('move_line_ids'):
                    line.write({'date': move.transfer_date or fields.Datetime.now()})
        elif stock_type_id.code in ('outgoing'):
            for move in res:
                move.write({'date': move.transfer_date or fields.Datetime.now()})
                for line in move.mapped('move_line_ids'):
                    line.write({'date': move.transfer_date or fields.Datetime.now()})
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:
            date = self.transfer_date or self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
            })
            new_account_move.post()
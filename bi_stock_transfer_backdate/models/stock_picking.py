# -*- coding : utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from  datetime import datetime
from odoo import SUPERUSER_ID
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError,Warning


class StockPickingUpdate(models.Model):
	_inherit = 'stock.picking'

	transfer_date = fields.Datetime(String="Transfer Date", copy=False)
	remark = fields.Char(String="Remarks", copy=False)

	def button_validate(self):
		if self.picking_type_id.code == 'outgoing':
			self.ensure_one()
			if not self.move_lines and not self.move_line_ids:
				raise UserError(_('Please add some lines to move'))
			super(StockPickingUpdate, self).button_validate()
			view = self.env.ref('bi_stock_transfer_backdate.view_change_stock_item')
			return {
					'binding_view_types': 'form',
					'view_mode': 'form',
					'res_model': 'change.module',
					'type': 'ir.actions.act_window',
					'target': 'new',
					'res_id': False,
					'context': self.env.context,
				}
		else:
			self.ensure_one()
			if not self.move_lines and not self.move_line_ids:
				raise UserError(_('Please add some items to move.'))

			# If no lots when needed, raise error
			picking_type = self.picking_type_id
			precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
			no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
			no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
			if no_reserved_quantities and no_quantities_done:
				raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

			if picking_type.use_create_lots or picking_type.use_existing_lots:
				lines_to_check = self.move_line_ids
				if not no_quantities_done:
					lines_to_check = lines_to_check.filtered(
						lambda line: float_compare(line.qty_done, 0,
												   precision_rounding=line.product_uom_id.rounding)
					)

				for line in lines_to_check:
					product = line.product_id
					if product and product.tracking != 'none':
						if not line.lot_name and not line.lot_id:
							raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

			# Propose to use the sms mechanism the first time a delivery
			# picking is validated. Whatever the user's decision (use it or not),
			# the method button_validate is called again (except if it's cancel),
			# so the checks are made twice in that case, but the flow is not broken
			sms_confirmation = self._check_sms_confirmation_popup()
			if sms_confirmation:
				return sms_confirmation

			if no_quantities_done:
				view = self.env.ref('stock.view_immediate_transfer')
				wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
				return {
					'name': _('Immediate Transfer?'),
					'type': 'ir.actions.act_window',
					'view_mode': 'form',
					'res_model': 'stock.immediate.transfer',
					'views': [(view.id, 'form')],
					'view_id': view.id,
					'target': 'new',
					'res_id': wiz.id,
					'context': self.env.context,
				}

			if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
				view = self.env.ref('stock.view_overprocessed_transfer')
				wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
				return {
					'type': 'ir.actions.act_window',
					'view_mode': 'form',
					'res_model': 'stock.overprocessed.transfer',
					'views': [(view.id, 'form')],
					'view_id': view.id,
					'target': 'new',
					'res_id': wiz.id,
					'context': self.env.context,
				}

			# Check backorder should check for other barcodes
			if self._check_backorder():
				return self.action_generate_backorder_wizard()
			self.action_done()
			return

	def action_done(self):
		"""Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
		self._check_company()

		todo_moves = self.mapped('move_lines').filtered(
			lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
		# Check if there are ops not linked to moves yet
		for pick in self:
			if pick.owner_id:
				pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
				pick.move_line_ids.write({'owner_id': pick.owner_id.id})

			# # Explode manually added packages
			# for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
			#     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
			#         self.move_line_ids.create({'product_id': quant.product_id.id,
			#                                    'package_id': quant.package_id.id,
			#                                    'result_package_id': ops.result_package_id,
			#                                    'lot_id': quant.lot_id.id,
			#                                    'owner_id': quant.owner_id.id,
			#                                    'product_uom_id': quant.product_id.uom_id.id,
			#                                    'product_qty': quant.qty,
			#                                    'qty_done': quant.qty,
			#                                    'location_id': quant.location_id.id, # Could be ops too
			#                                    'location_dest_id': ops.location_dest_id.id,
			#                                    'picking_id': pick.id
			#                                    }) # Might change first element
			# # Link existing moves or add moves when no one is related
			for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
				# Search move with this product
				moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
				moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
				if moves:
					ops.move_id = moves[0].id
				else:
					new_move = self.env['stock.move'].create({
						'name': _('New Move:') + ops.product_id.display_name,
						'product_id': ops.product_id.id,
						'product_uom_qty': ops.qty_done,
						'product_uom': ops.product_uom_id.id,
						'description_picking': ops.description_picking,
						'location_id': pick.location_id.id,
						'location_dest_id': pick.location_dest_id.id,
						'picking_id': pick.id,
						'picking_type_id': pick.picking_type_id.id,
						'restrict_partner_id': pick.owner_id.id,
						'company_id': pick.company_id.id,
					})
					ops.move_id = new_move.id
					new_move._action_confirm()
					todo_moves |= new_move
				# 'qty_done': ops.qty_done})

		todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder',False))
		self.write({'date_done': fields.Datetime.now()})
		self._send_confirmation_email()
		return True

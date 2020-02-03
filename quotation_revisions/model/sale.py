# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _rec_name = 'rec_name'
    
    number_of_revision = fields.Integer(string='Revision History', compute='_get_number_of_revision')
    is_revision = fields.Boolean(string='Is Revision', default=False, copy=False)
    rev_number = fields.Char(string='Rev Number', copy=True, readonly=True)
    revision_number = fields.Char('Rev Number', copy=False)
    rec_name = fields.Char(string='Rev Number', compute='_get_name', store=True)
    is_confirmed = fields.Boolean(string='Is Confirmed', default=False, copy=False)

    _sql_constraints = [('name_rev_number_uniq', 'UNIQUE(name, rev_number)', 'Order Reference must be unique per Revision Number')]
    
    @api.depends('rev_number')
    def _get_name(self):
        if not self.rev_number == False:
            self.rec_name = self.name + ' ' + self.rev_number
        else:
            self.rec_name = self.name
            
    
    def action_make_revision(self):
        copied_rec = self.copy()
        sequence_obj = self.env['ir.sequence'].search([('code', '=', 'sale.order')],limit=1)
        sequence_obj.number_next_actual = sequence_obj.number_next_actual - 1 
        copied_rec.name = self.name
        if self.rev_number == False:
            rev_number = 1
            copied_rec.rev_number = 'Rev ' + str(rev_number)
        else:
            rev_number = int(self.rev_number[4:]) + 1
            copied_rec.rev_number = 'Rev ' + str(rev_number)
        self.is_revision = True
        copied_rec.revision_number = copied_rec.rev_number[4:]
        ctx = dict(self.env.context)
        return {
                'name': _('Sale Orders'),
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'sale.order',
                'res_id': copied_rec.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                }
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if self.rev_number:
            default['rev_number'] = False
        return super(SaleOrder, self).copy(default)

    def unlink(self):
        for record in self:
            if record.state == 'cancel' and record.is_revision == True:
                raise UserError(_('You can not delete sale order once its have a revision.'))
            return super(SaleOrder, record).unlink()
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            if so.picking_ids and self.rev_number:
                for pick in so.picking_ids:
                    pick.origin = so.name + ' ' + so.rev_number
            so.is_confirmed = True
        return res
    
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.rev_number:
            res['origin'] = self.name + ' ' + self.rev_number
        return res
    
    def view_so_revision_history(self):
        so_ids = self.search([('name', '=', self.name)]).ids
        return {
            'name': _('Revision History'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', so_ids)],
        }
        
    def _get_number_of_revision(self):
        self.number_of_revision = len(self.search([('name', '=', self.name)]).ids) - 1

        
class SaleAdvancePayment(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePayment, self)._create_invoice(order, so_line, amount)
        if order.rev_number:
            res.origin = order.name + ' ' + order.rev_number
        return res
    

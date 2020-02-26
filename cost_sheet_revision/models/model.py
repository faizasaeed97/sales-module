# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

import  datetime
class Costsheets(models.Model):
    _inherit = 'cost.sheet.crm'
    _rec_name = 'name'


    is_a_revision = fields.Boolean(default=False)
    number_of_revision = fields.Integer(string='Revision History', compute='_get_number_of_revision')
    is_revision = fields.Boolean(string='Is Revision', default=False, copy=False)
    rev_number = fields.Char(string='Rev Number', copy=True, readonly=True)
    revision_number = fields.Char('Rev Number', copy=False)
    rec_name = fields.Char(string='Rev Number', compute='_get_name', store=True)
    is_confirmed = fields.Boolean(string='Is Confirmed', default=False, copy=False)
    cost_sheet_rev_id = fields.Many2one('cost.sheet.crm')


    def view_cs_revision_history(self):
        so_ids = self.search([('name', '=', self.name),('is_revision', '=', True)]).ids
        return {
            'name': _('Revision History'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cost.sheet.crm',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', so_ids)],
        }





    def create_revision(self):
        copied_rec = self.copy()
        sequence_obj = self.env['ir.sequence'].search([('code', '=', 'cost.sheet.crm')], limit=1)
        sequence_obj.number_next_actual = sequence_obj.number_next_actual - 1
        copied_rec.name = self.name
        if self.rev_number == False:
            rev_number = 1
            copied_rec.rev_number = 'Rev ' + str(rev_number)
        else:
            rev_number = int(self.rev_number[4:]) + 1
            copied_rec.rev_number = 'Rev ' + str(rev_number)

        copied_rec.cost_sheet_date=self.cost_sheet_date
        copied_rec.client =self.client
        copied_rec.sale_person =self.sale_person
        copied_rec.material_ids =self.material_ids
        copied_rec.labor_ids =self.labor_ids
        copied_rec.overhead_ids =self.overhead_ids
        copied_rec.rental_ids =self.rental_ids
        copied_rec.material_total =self.material_total
        copied_rec.labor_total =self.labor_total
        copied_rec.overhead_total =self.overhead_total

        copied_rec.rental_total =self.rental_total
        copied_rec.grand_total =self.grand_total
        copied_rec.markup_type =self.markup_type
        copied_rec.quotation_value =self.quotation_value
        copied_rec.markup_value =self.markup_value
        copied_rec.company_currency =self.company_currency
        copied_rec.scope_work =self.scope_work


        copied_rec.is_a_revision = True
        copied_rec.number_of_revision = self.number_of_revision
        copied_rec.is_revision = True



        self.is_revision = True
        copied_rec.is_a_revision = True
        copied_rec.revision_number = copied_rec.rev_number[4:]
        ctx = dict(self.env.context)
        return {
            'name': _('Cost Sheet'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'cost.sheet.crm',
            'res_id': copied_rec.id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    @api.depends('rev_number')
    def _get_name(self):
        for record in self:
            if not record.rev_number == False:
                record.rec_name = self.name + ' ' + record.rev_number
            else:
                record.rec_name = record.name

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if self.rev_number:
            default['rev_number'] = False
        return super(Costsheets, self).copy(default)

    def unlink(self):
        for record in self:
            if record.is_revision == True:
                raise UserError(_('You can not delete Cost Sheet once its have a revision.'))
            return super(Costsheets, record).unlink()

    def view_so_revision_history(self):
        so_ids = self.search([('name', '=', self.name)]).ids
        return {
            'name': _('Revision History'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cost.sheet.crm',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', so_ids)],
        }

    def _get_number_of_revision(self):
        self.number_of_revision = len(self.search([('name', '=', self.name)]).ids) - 1





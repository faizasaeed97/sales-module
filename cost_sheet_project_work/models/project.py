from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import itertools


class Costsheet(models.Model):
    _inherit = 'project.project'

    additional_costsheet_count = fields.Integer(string='Costsheet_revisioncount', compute='get_additional_costsheet')
    cost_sheet_revision_count = fields.Integer(string='Costsheet_revisioncount', compute='get_costsheetrevision_count')
    po_count= fields.Integer(string='po count', compute='get_po_count')

    def get_costsheetrevision_count(self):
        if self.id:
            # how can we compute this ???
            # check project reference in sale, get ks se yeh hoe ha sale costsheet, then us costsheet ke additional cost sheet get
            for rec in self:
                # sale_order = self.env['sale.order'].search([('project', '=', self.id)], limit=1)

                cost_sheet_revision_count = self.env['cost.sheet.crm']. \
                    search_count([('is_a_revision', '=', True),
                                  ('opportunity_id', '=', self.id)])
                if cost_sheet_revision_count:
                    rec.cost_sheet_revision_count = cost_sheet_revision_count
                else:
                    rec.cost_sheet_revision_count = 0

    def get_po_count(self):
        if self.id:
            # how can we compute this ???
            # check project reference in sale, get ks se yeh hoe ha sale costsheet, then us costsheet ke additional cost sheet get
            for rec in self:
                # sale_order = self.env['sale.order'].search([('project', '=', self.id)], limit=1)

                pocount = self.env['purchase.order']. \
                    search_count([('project.id', '=', self.id)])
                if pocount:
                    rec.po_count = pocount
                else:
                    rec.po_count = 0


    def get_additional_costsheet(self):
        if self.id:
            # how can we compute this ???
            # check project reference in sale, get ks se yeh hoe ha sale costsheet, then us costsheet ke additional cost sheet get
            for rec in self:
                # sale_order = rec.env['sale.order'].search([('project.id', '=', rec.id)], limit=1)
                # if sale_order:
                    # get cost sheetref
                cost_sheet_additional_count = rec.env['cost.sheet.crm']. \
                    search_count([('is_additional', '=', True), ('opportunity_id.id', '=', rec.id)])
                if cost_sheet_additional_count and cost_sheet_additional_count > 0:
                    rec.additional_costsheet_count = cost_sheet_additional_count
                else:
                    rec.additional_costsheet_count = 0
                    return 0
                # else:
                #     rec.additional_costsheet_count = 0
                #     return 0

    def view_additional_history(self):
        lists = []
        cost_sheet_additional_count = self.env['cost.sheet.crm']. \
            search(
            [('is_additional', '=', True), ('opportunity_id.id', '=', self.id)])

        out = list(itertools.chain(*cost_sheet_additional_count))

        for o in out:
            for z in o:
                lists.append(z.id)

        if lists:
            return {
                'name': _('Additional History'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'cost.sheet.crm',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', lists)],
            }
        else:
            return 0

    def view_rev_history(self):
            lists = []
            cost_sheet_additional_count = self.env['cost.sheet.crm'].search([('is_a_revision', '=', True), ('opportunity_id.id', '=', self.id)])

            out = list(itertools.chain(*cost_sheet_additional_count))

            for o in out:
                for z in o:
                    lists.append(z.id)

            if lists:
                return {
                    'name': _('Revision History'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'cost.sheet.crm',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', lists)],
                }
            else:
                return 0

    def view_po_history(self):
        lists = []
        pocnt = self.env['purchase.order'].search(
            [('project.id', '=', self.id)])

        out = list(itertools.chain(*pocnt))

        for o in out:
            for z in o:
                lists.append(z.id)

        if lists:
            return {
                'name': _('Hurchase History'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', lists)],
            }
        else:
            return 0




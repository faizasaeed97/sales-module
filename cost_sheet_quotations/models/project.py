from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class Costsheet(models.Model):
    _inherit = 'project.project'

    additional_costsheet_count = fields.Integer(string='Costsheet_revisioncount',compute='get_additional_costsheet')

    cost_sheet_revision_count = fields.Integer(string='Costsheet_revisioncount',compute='get_costsheetrevision_count')


    def get_costsheetrevision_count(self):
        if self.id:
            # how can we compute this ???
            # check project reference in sale, get ks se yeh hoe ha sale costsheet, then us costsheet ke additional cost sheet get
            sale_order = self.env['sale.order'].search([('project', '=', self.id)], limit=1)
            if sale_order:
                # get cost sheetref
                cost_sheet_revision_count = self.env['cost.sheet.crm']. \
                    search_count([('is_a_revision','=',True),('parent_cost_sheet_ref', '=', False),
                                  ('opportunity_id', '=', self.get_opportunity_name_byid(self.name))])
            self.cost_sheet_revision_count=cost_sheet_revision_count

    def get_opportunity_name_byid(self,name):
        opportunity= self.env['crm.lead'].search([('name','=',name)])
        if opportunity:
            return opportunity.id
    def get_additional_costsheet(self):
        if self.id:
            # how can we compute this ???
            # check project reference in sale, get ks se yeh hoe ha sale costsheet, then us costsheet ke additional cost sheet get
            sale_order = self.env['sale.order'].search([('project','=',self.id)],limit=1)
            if sale_order:
                # get cost sheetref
                cost_sheet_additional_count = self.env['cost.sheet.crm'].\
                    search_count([('parent_cost_sheet_ref', '!=',False),('opportunity_id','=',self.get_opportunity_name_byid(self.name))])
                if cost_sheet_additional_count:
                    self.additional_costsheet_count=cost_sheet_additional_count



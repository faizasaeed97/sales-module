from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class Costsheet(models.Model):
    _inherit = 'product.template'

    raw_mat = fields.Boolean(string='Raw Material')
    final_prod = fields.Boolean(string='Final Product')



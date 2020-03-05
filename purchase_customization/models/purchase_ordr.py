from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class purchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project = fields.Many2one('project.project',string='Project')

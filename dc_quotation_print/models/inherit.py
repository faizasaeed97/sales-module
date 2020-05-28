from odoo import api, fields, models

class DCQuotationSaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    quotation_subject = fields.Char("Quotation Subject")
    validity_days = fields.Integer("Valid For (Days)")
    delivery = fields.Char("Delivery")

class DCQuotationScopeWorkLine(models.Model):
    _inherit = "scope.work.line"
    work_scope = fields.Text("Scope Of Work")
    zones = fields.Many2one("sale.order.zones", string="Zone")

class DCQuotationZonesSelection(models.Model):
    _name = "sale.order.zones"

    name = fields.Char("Zona Name")
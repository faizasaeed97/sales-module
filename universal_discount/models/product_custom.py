from odoo import models, fields, api


class brandclas(models.Model):
    _name = 'brand'

    name=fields.Char("Brand")



class inheritprodx(models.Model):
    _inherit = 'product.template'


    brand= fields.Many2many('brand', string='Brand')




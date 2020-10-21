from odoo import api, fields, models, _

class MROAProductReference(models.Model):
    _name = 'mroa.product.reference.price'
    _description = 'Product Reference Price'

    @api.depends('inflation_rates', 'last_reference_price')
    def calculate_infalation_rates(self):
        for record in self:
            counter = 0
            lrp_current_year = 0
            for line in record.inflation_rates:
                if counter == 0:
                    lrp = record.last_reference_price
                    if record.estimated_price:
                        lrp = record.estimated_price_value
                    lrp_current_year = (1 + (line.infaltion_rate / 100)) * lrp
                    self.env['product.inflation.rate.model'].browse(line.id).write({'lrp_current_year': lrp_current_year})
                else:
                    lrp_current_year = (1 + (line.infaltion_rate / 100)) * lrp_current_year
                    self.env['product.inflation.rate.model'].browse(line.id).write({'lrp_current_year': lrp_current_year})
                counter += 1

    @api.depends('product_id')
    def compute_purchase_year(self):
        for record in self:
            if record.product_id:
                results = self.env['purchase.order.line'].search([('product_id','=',record.product_id.product_variant_id.id)], order="id desc", limit=1)
                if results:
                    record.purchase_year = str(results.create_date.year)
                    record.last_reference_price = results.price_unit
                    record.name = results.product_id.name
                else:
                    record.purchase_year = ""
            else:
                record.purchase_year = ""

    def write(self, vals):
        getit = super(MROAProductReference, self).write(vals)
        if 'last_reference_price' in vals or 'estimated_price' in vals:
            self.calculate_infalation_rates()
        return getit

    name = fields.Char("Name")
    product_id = fields.Many2one("product.template", string="Select Part")
    last_reference_price = fields.Float("Last Reference Price(LRP OR Cost)", compute="calculate_infalation_rates",readonly=False, store=True)
    purchase_currency = fields.Many2one("res.currency", string="Currency Of Purchase")
    purchase_year = fields.Char("Year Of Purchase", compute="compute_purchase_year", readonly=False, store=True)
    procurement_condition = fields.Many2one("product.tail.procurement.condition", string="Procurement Condition")
    inflation_rates = fields.One2many("product.inflation.rate.model", 'reference_id', string="Inflation Rates")
    estimated_price = fields.Boolean("Estimated Price")
    estimated_price_value = fields.Float("Estimated Price")

class ProductInflationRateModel(models.Model):
    _name = "product.inflation.rate.model"

    @api.model
    def create(self, vals):
        if 'infaltion_rate' in vals and 'prod_tmp_id' in vals:
            getit = self.env['product.inflation.rate.model'].search([('reference_id', '=', vals['reference_id'])],order="id desc", limit=1)
            lrp_current_year = 0
            if getit:
                lrp_current_year = (1 + (vals['infaltion_rate'] / 100)) * getit.lrp_current_year
            else:
                get = self.env['product.template'].browse(vals['prod_tmp_id']).last_reference_price
                lrp_current_year = (1 + (vals['infaltion_rate'] / 100)) * get

            vals['lrp_current_year'] = lrp_current_year
        return super(ProductInflationRateModel, self).create(vals)

    inflation_year = fields.Char("Year Of Inflation")
    currency = fields.Many2one("res.currency")
    infaltion_rate = fields.Float("Inflation Rate (%)")
    lrp_current_year = fields.Float("LRP Current Year")
    reference_id = fields.Many2one("mroa.product.reference.price", string="Product ID")
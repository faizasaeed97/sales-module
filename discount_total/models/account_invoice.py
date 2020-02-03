from odoo import models, fields, api
from odoo.sql_db import TestCursor



class AccountInvoice(models.Model):
    _inherit = 'account.move'


    @api.depends('invoice_line_ids.price_subtotal', 'currency_id', 'company_id', 'invoice_date', 'type')
    def compute_discount(self):
        round_curr = self.currency_id.round
        if self:
            for rec in self:
                rec.amount_untaxed = sum(line.price_subtotal for line in rec.invoice_line_ids)
                # self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_id)
                # self.amount_total = self.amount_untaxed+self.amount_tax
                discount = 0
                for line in rec.invoice_line_ids:
                    discount += (line.price_unit * line.quantity * line.discount) / 100
                rec.discount = discount
                rec.amount_tax = sum(round_curr((line.tax_ids.amount*line.price)/100) for line in rec.invoice_line_ids)

                rec.amount_total=(rec.amount_untaxed+rec.amount_tax)
                amount_total_company_signed = rec.amount_total
                amount_untaxed_signed = rec.amount_untaxed
                if rec.currency_id and rec.company_id and rec.currency_id != rec.company_id.currency_id:
                    currency_id = rec.currency_id.with_context(date=rec.invoice_date)
                    amount_total_company_signed = currency_id.compute(rec.amount_total, rec.company_id.currency_id)
                    amount_untaxed_signed = currency_id.compute(rec.amount_untaxed, rec.company_id.currency_id)
                sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
                rec.amount_total_company_signed = amount_total_company_signed * sign
                rec.amount_total_signed = rec.amount_total * sign
                rec.amount_untaxed_signed = amount_untaxed_signed * sign



    @api.depends('invoice_line_ids')
    def compute_total_before_discount(self):
        for rec in self:
            total = 0
            for line in rec.invoice_line_ids:
                total += line.price
            rec.total_before_discount = total

    @api.depends('invoice_line_ids')
    def compute_total_after_discount(self):
        for rec in self:
            total = 0
            total =  rec.total_before_discount - rec.discount
            rec.total_after_discount = total


    # discount_type = fields.Selection([('percentage', 'Percentage')], string='Discount Type',
    #                                  readonly=True, states={'draft': [('readonly', False)]}, default='percentage')
    # discount_rate = fields.Float(string='Discount Rate', digits=(16, 2),
    #                              readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    discount = fields.Monetary(string='Discount', digits=(16, 2), default=0.0,
                               store=True, compute='compute_discount', track_visibility='always')
    total_before_discount = fields.Monetary(string='Total Before Discount', digits=(16, 2), store=True, compute='compute_total_before_discount')

    total_after_discount = fields.Monetary(string='Total After Discount', digits=(16, 2), store=True, compute='compute_total_after_discount')




    # @api.onchange('discount_type', 'discount_rate', 'invoice_lines_ids')
    # def set_lines_discount(self):
    #     discount=0
    #     if self.discount_type == 'percentage':
    #         for line in self.invoice_line_ids:
    #             line.discount=self.discount_rate
    #             line.price_subtotal = (line.quantity * line.price_unit) - ((line.quantity * line.price_unit * line.discount) / 100)
    #             discount += (line.price_unit * line.quantity * line.discount) / 100
    #
    #         self.discount = discount
    #         self.total_after_discount=self.total_before_discount-discount
    #         self.amount_total = self.amount_total - discount

            # self.write(self.record, 'A')

        # else:
        #     total = discount = 0.0
        #     for line in self.invoice_line_ids:
        #         total += (line.quantity * line.price_unit)
        #     if self.discount_rate != 0:
        #         discount = (self.discount_rate / total) * 100
        #     else:
        #         discount = self.discount_rate
        #     for line in self.invoice_line_ids:
        #         line.discount = discount
        #         # line.price=line.price-line.discount



    # def button_dummy(self):
    #     for rec in self:
    #         rec.set_lines_discount()
    #     return True


    # def write(self, vals):
    #
    #     if 'discount_rate' in vals:
    #         round_curr = self.currency_id.round
    #
    #         discount=0.0
    #         if self.discount_type == 'percentage':
    #             for line in self.invoice_line_ids:
    #                 line.price_subtotal= (line.price_unit * line.quantity) -((line.price_unit * line.quantity * vals['discount_rate'])/100)
    #                 line.discount = vals['discount_rate']
    #                 discount += (line.price_unit * line.quantity * line.discount) / 100
    #                 # line.price = line.price_subtotal - ((self.discount_rate * line.price_subtotal) / 100)
    #
    #             # vals['discount'] = discount
    #             vals['total_after_discount'] = self.total_before_discount - discount
    #             amount_tax = sum(round_curr((line.tax_ids.amount*line.price)/100) for line in self.invoice_line_ids)
    #
    #             vals['amount_total'] = (self.total_after_discount+amount_tax)
    #             vals['total_before_discount']=self.total_before_discount
    #     res = super(AccountInvoice, self).write(vals)
    #
    # @api.model_create_multi
    # def create(self, vals_list):
    #
    #     res = super(AccountInvoice, self).create(vals_list)
    #     round_curr = res.currency_id.round
    #     if vals_list:
    #         discount = 0.0
    #
    #         if 'discount_rate' in vals_list or 'discount_rate' in vals_list[0] :
    #             if vals_list[0]['discount_type'] == 'percentage':
    #                 for line in res.invoice_line_ids:
    #                     line.discount = res.discount_rate
    #                     discount += (line.price_unit * line.quantity * line.discount) / 100
    #                     # line.price = line.price_subtotal - ((self.discount_rate * line.price_subtotal) / 100)
    #
    #                 res.total_after_discount = res.total_before_discount - discount
    #                 amount_tax = sum(round_curr((line.tax_ids.amount*line.price_subtotal)/100) for line in res.invoice_line_ids)
    #
    #                 res.amount_total= (res.total_after_discount+amount_tax)
    #         else:
    #             for line in res.invoice_line_ids:
    #                 line.discount = res.discount_rate
    #                 discount += (line.price_unit * line.quantity * line.discount) / 100
    #                 # line.price = line.price_subtotal - ((self.discount_rate * line.price_subtotal) / 100)
    #
    #             res.total_after_discount = res.total_before_discount - discount
    #             amount_tax = sum(
    #                 round_curr((line.tax_ids.amount * line.price_subtotal) / 100) for line in res.invoice_line_ids)
    #
    #             res.amount_total = (res.total_after_discount + amount_tax)
    #
    #
    #     return res
                # vals_list[0]['total_before_discount']=res.total_before_discount



#
class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"


    @api.depends('quantity', 'price_unit')
    def compute_line_price(self):
        for r in self:
            r.price = (r.quantity * r.price_unit)




    # discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    price = fields.Float(string='Price', digits=(16, 2), store=True, compute='compute_line_price')

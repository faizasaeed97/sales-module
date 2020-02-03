from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class purchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.depends('order_line.price_subtotal', 'order_line.price_tax','currency_id', 'company_id', 'date_order')
    def compute_discount(self):
        for rec in self:
            round_curr = rec.currency_id.round
            rec.amount_untaxed = sum(line.price_subtotal for line in rec.order_line)
            rec.amount_tax = sum(round_curr((line.taxes_id.amount*line.price_subtotal)/100) for line in rec.order_line)
            discount = 0
            for line in rec.order_line:
                line.discount=rec.discount_rate
                discount += (line.price_unit * line.product_qty * line.discount) / 100

            rec.discount = discount

            rec.total_before_discount=rec.amount_untaxed
            rec.total_after_discount=rec.total_before_discount-discount

            rec.amount_total = rec.total_after_discount + rec.amount_tax

            amount_total_company_signed = rec.amount_total
            amount_untaxed_signed = rec.amount_untaxed
            if rec.currency_id and rec.company_id and rec.currency_id != rec.company_id.currency_id:
                currency_id = rec.currency_id.with_context(date=rec.date_order)
                amount_total_company_signed = currency_id.compute(rec.amount_total, rec.company_id.currency_id)
                amount_untaxed_signed = currency_id.compute(rec.amount_untaxed, rec.company_id.currency_id)
            rec.amount_total_company_signed = amount_total_company_signed
            rec.amount_total_signed = rec.amount_total
            rec.amount_untaxed_signed = amount_untaxed_signed


    @api.depends('order_line')
    def compute_total_before_discount(self):
        total = 0
        for line in self.order_line:
            total += line.price_subtotal
        self.total_before_discount = total
    #
    # amount_untaxed = fields.Float(string='Untaxed Amount', store=True, readonly=True, tracking=True,
    #                                  compute='_compute_amount')

    discount_type = fields.Selection([('percentage', 'Percentage')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='percentage')
    discount_rate = fields.Float(string='Discount Rate', digits=(16, 2),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default=0.0)
    discount = fields.Monetary(string='Discount', digits=(16, 2), default=0.0,
                               store=True, compute='compute_discount', track_visibility='always')
    total_before_discount = fields.Monetary(string='Total Before Discount', digits=(16, 2), store=True, compute='compute_total_before_discount')

    total_after_discount = fields.Monetary(string='Total After Discount', digits=(16, 2), store=True, compute='compute_total_after_discount')


    # @api.depends('order_line')
    def compute_total_after_discount(self):
        for rec in self:
            total = 0
            total =  rec.total_before_discount - rec.discount
            rec.total_after_discount = total


    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def set_lines_discount(self):
        total = discount = 0.0
        round_curr = self.currency_id.round

        if self.discount_type == 'percentage':
            for line in self.order_line:
                line.discount=self.discount_rate
                discount += (line.price_unit * line.product_qty * line.discount) / 100
            self.discount = discount
            self.total_after_discount = self.total_before_discount - discount
            amount_tax = sum(round_curr((line.taxes_id.amount*line.price_subtotal)/100) for line in self.order_line)
            self.amount_total = (self.total_after_discount)+amount_tax
        # else:
        #     for line in self.order_line:
        #         total += (line.product_uom_qty * line.price_unit)
        #     if self.discount_rate != 0:
        #         discount = (self.discount_rate / total) * 100
        #     else:
        #         discount = self.discount_rate
        #     for line in self.order_line:
        #         line.discount = discount


    def button_dummy(self):
        self.set_lines_discount()
        return True
    #

    def write(self, vals):

        if 'discount_rate' in vals:
            round_curr = self.currency_id.round

            discount=0.0
            if self.discount_type == 'percentage':
                for line in self.order_line:
                    line.discount=vals['discount_rate']
                    discount += ((line.price_unit * line.product_qty * vals['discount_rate']) / 100)
                    # line.price = line.price_subtotal - ((self.discount_rate * line.price_subtotal) / 100)

                vals['discount'] = discount
                vals['total_after_discount'] = self.total_before_discount - discount
                amount_tax = sum( round_curr((line.taxes_id.amount * line.price_subtotal) / 100) for line in self.order_line)

                vals['amount_total'] = (self.total_after_discount-discount)+amount_tax
                vals['total_before_discount']=self.total_before_discount
        res = super(purchaseOrder, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):

        res = super(purchaseOrder, self).create(vals_list)
        round_curr = res.currency_id.round

        if 'discount_rate' in vals_list[0]:
            discount = 0.0
            if vals_list[0]['discount_type'] == 'percentage':
                for line in res.order_line:
                    line.discount=res.discount_rate
                    discount += (line.price_unit * line.product_qty * line.discount) / 100
                    # line.price = line.price_subtotal - ((self.discount_rate * line.price_subtotal) / 100)

                # vals['discount'] = discount
                res.total_after_discount = res.total_before_discount - discount
                amount_tax = sum(round_curr((line.taxes_id.amount * line.price_subtotal) / 100) for line in res.order_line)

                res.amount_total = (res.total_after_discount + amount_tax)

        return res



    # def action_invoice_create(self, grouped=False, final=False):
    #     inv_obj = self.env['account.move']
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     invoices = {}
    #     references = {}
    #     invoices_origin = {}
    #     invoices_name = {}
    #
    #     for order in self:
    #         group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
    #         for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
    #             if float_is_zero(line.qty_to_invoice, precision_digits=precision):
    #                 continue
    #             if group_key not in invoices:
    #                 inv_data = order._prepare_invoice()
    #                 invoice = inv_obj.create(inv_data)
    #                 references[invoice] = order
    #                 invoices[group_key] = invoice
    #                 invoices_origin[group_key] = [invoice.origin]
    #                 invoices_name[group_key] = [invoice.name]
    #             elif group_key in invoices:
    #                 if order.name not in invoices_origin[group_key]:
    #                     invoices_origin[group_key].append(order.name)
    #                 if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
    #                     invoices_name[group_key].append(order.client_order_ref)
    #
    #             if line.qty_to_invoice > 0:
    #                 line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
    #             elif line.qty_to_invoice < 0 and final:
    #                 line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
    #
    #         if references.get(invoices.get(group_key)):
    #             if order not in references[invoices[group_key]]:
    #                 references[invoices[group_key]] |= order
    #
    #     for group_key in invoices:
    #         invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
    #                                    'origin': ', '.join(invoices_origin[group_key])})
    #
    #     if not invoices:
    #         raise UserError(_('There is no invoiceable line.'))
    #
    #     for invoice in invoices.values():
    #         if not invoice.invoice_line_ids:
    #             raise UserError(_('There is no invoiceable line.'))
    #         # If invoice is negative, do a refund invoice instead
    #         if invoice.amount_untaxed < 0:
    #             invoice.type = 'out_refund'
    #             for line in invoice.invoice_line_ids:
    #                 line.quantity = -line.quantity
    #         # Use additional field helper function (for account extensions)
    #         for line in invoice.invoice_line_ids:
    #             line._set_additional_fields(invoice)
    #         # Necessary to force computation of taxes. In account_invoice, they are triggered
    #         # by onchanges, which are not triggered when doing a create.
    #         invoice.compute_taxes()
    #         invoice.message_post_with_view('mail.message_origin_link',
    #                                        values={'self': invoice, 'origin': references[invoice]},
    #                                        subtype_id=self.env.ref('mail.mt_note').id)
    #
    #         if order.discount_rate > 0:
    #             invoice.discount_rate = order.discount_rate
    #     return [inv.id for inv in invoices.values()]

#
class SaleOrderLine(models.Model):
    _inherit = "purchase.order.line"
    #
    # @api.depends('product_uom_qty', 'price_unit')
    # def compute_line_price(self):
    #     for rec in self:
    #         rec.price = rec.product_qty * rec.price_unit

    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    # price = fields.Float(string='Price', digits=(16, 2), store=True, compute='compute_line_price')

    def _prepare_account_move_line(self, move):
        self.ensure_one()
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id


        return {
            'name': '%s: %s' % (self.order_id.name, self.name),
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'purchase_line_id': self.id,
            'date_maturity': move.invoice_date_due,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount':self.discount,
            'partner_id': move.partner_id.id,
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'display_type': self.display_type,
        }

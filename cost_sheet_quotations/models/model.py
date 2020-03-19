# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

import datetime


class Costsheet(models.Model):
    _name = 'cost.sheet.crm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    is_quotation_generated = fields.Boolean()
    is_additional = fields.Boolean()
    # parent_cost_sheet_ref = fields.Many2one('cost.sheet.crm',string='Costsheet ref')
    opportunity_id = fields.Many2one('project.project', string='Project')
    crm_lead=fields.Many2one('crm.lead', string='lead')
    dafult_cost_sheet_ref = fields.Many2one('cost.sheet.crm', string='Costsheet ref',readonly=False)
    name = fields.Char(string='Cost sheet No.')
    cost_sheet_date = fields.Date(string='Date', default=fields.Datetime.now().date())
    client = fields.Many2one('res.partner', string='Client')
    sale_person = fields.Many2one('res.users', string='Sales person',default=lambda self: self.env.user)
    material_ids = fields.One2many('cost.sheet.material', 'cost_sheet',store=True,copy=True, ondelete='cascade')
    labor_ids = fields.One2many('cost.sheet.labors', 'cost_sheet',store=True,copy=True, ondelete='cascade')
    overhead_ids = fields.One2many('cost.sheet.overhead', 'cost_sheet',store=True,copy=True, ondelete='cascade')
    internal_rental_ids = fields.One2many('cost.sheet.rental.internal', 'cost_sheet',store=True,copy=True, ondelete='cascade')

    outsource_rental_ids = fields.One2many('cost.sheet.rental.outsource', 'cost_sheet',store=True,copy=True, ondelete='cascade')

    initial_budget = fields.Float(string="initial budget", compute="get_costsheet_summery", )
    cs_history_value = fields.Float(string="Cost Sheet history", compute="get_costsheet_summery", )

    auctual_budget = fields.Float(string="auctual budget", compute="get_costsheet_summery", )
    quotation_value = fields.Float(string="Quotation value", compute="get_costsheet_summery")
    final_profit = fields.Float(string="Final profit", compute="get_costsheet_summery",digits=(16, 2))

    material_total = fields.Float(compute='material_total_cal',store=True)
    labor_total = fields.Float(compute='labor_total_cal',store=True)
    overhead_total = fields.Float(compute='overhead_total_cal',store=True)
    rental_total = fields.Float(compute='rental_total_cal',store=True)
    rental_total_out=fields.Float(compute='rental_total_cal_out',store=True)
    grand_total = fields.Float(compute='grand_total_cal')
    markup_type = fields.Selection([('Percentage', 'Percentage'), ('Amount', 'Amount')], default='Percentage',
                                   string='Markup Type')
    quotation_value = fields.Float(string='Quotation Value', compute='get_quotation_value')
    markup_value = fields.Float(string='Markup Value')
    company_id = fields.Many2one('res.company', string='Company', readonly=False,
                                 default=lambda self: self.env.company)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")
    closing_estimation_target =fields.Date(string="Estimate Closing Date")

    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Validated', 'Validated'),
        ('Approved', 'Approved'),
    ], string="State", default='Draft', track_visibility='onchange', copy=False, )

    quotation_count = fields.Integer(string="Quotations",)

    scope_work = fields.One2many('scope.work', 'cost_sheet',store=True,copy=True)

    is_final_cs=fields.Boolean("Final Cost Sheet?",default=False,)



    def get_costsheet_summery(self):
        cost_sheetx = self.env['cost.sheet.crm'].search(
            [('name', '=', self.name), ('is_a_revision', '=', False)])
        if  cost_sheetx:
            # means this cost shet has revisions
            self.initial_budget= cost_sheetx.grand_total
            self.cs_history_value=0.0
            cs_history=self.env['cost.sheet.crm'].search([('dafult_cost_sheet_ref.id','=', cost_sheetx.id),('is_a_revision','=',True)])
            grand_totalx=0.0
            for rec in cs_history:
                grand_totalx += (rec.material_total + rec.labor_total + rec.overhead_total + rec.rental_total+rec.rental_total_out)

            self.cs_history_value=grand_totalx

            final_cs=self.env['cost.sheet.crm'].search([('dafult_cost_sheet_ref.id','=', cost_sheetx.id),('is_final_cs','=',True)])
            auctual_budget=0.0
            final_quotation=0.0
            profit=0.0
            if len(final_cs)==1:
                auctual_budget=final_cs.grand_total
                final_quotation=final_cs.quotation_value
                profit=final_quotation-auctual_budget

            else:
                last_cs = self.env['cost.sheet.crm'].search(
                    [('dafult_cost_sheet_ref.id', '=',  cost_sheetx.id)],limit=1,order='id desc')

                if last_cs:
                    auctual_budget = last_cs.grand_total
                    final_quotation = last_cs.quotation_value
                    profit = final_quotation - auctual_budget
                else:
                    auctual_budget = self.grand_total
                    final_quotation = self.quotation_value
                    profit = final_quotation - auctual_budget


            self.auctual_budget=auctual_budget
            self.quotation_value=final_quotation
            self.final_profit=profit

        elif not  cost_sheetx:
            # means this cost shet has no revision
                self.initial_budget = self.grand_total
                self.cs_history_value = self.grand_total
                self.auctual_budget = self.grand_total
                self.quotation_value = self.quotation_value
                profit = self.quotation_value - self.auctual_budget
                self.final_profit = profit



    def approve_cs(self):
        self.state='Approved'

    def validate_cs(self):
        self.state='Validated'

    def reset_todraft(self):
        self.state='Draft'

    def get_projectid_byname(self, name):
        project = self.env['project.project'].search([('name', '=', name)])
        if project:
            return project.id

    def check_if_saleordercocnfirm(self, project_name):
        # check is project ke name se saleorde bna hoa tu not allow error
        sale_order = self.env['sale.order'].search(
            [('state', 'in', ['sale', 'lock']), ('project.id', '=', self.opportunity_id.id)])
        if sale_order:
            return True
        else:
            return False

    def create_additional_cost_sheet(self):
        # if self.check_if_saleordercocnfirm(self.opportunity_id.name):
        #     raise ValidationError("you can't create addional costsheet, cancel confirm sale order first")

        view_id = self.env.ref('cost_sheet_quotations.costsheet_form')
        return {
            'name': _('Costsheet'),
            'view_id': view_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cost.sheet.crm',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'is_additional': True,
                'default_parent_cost_sheet_ref': self.id,
                'default_opportunity_id': self.opportunity_id.id
            },
        }

    def get_markup_amount(self, grand_total, markup_type, markup_val):
        if markup_type == 'Amount':
            return markup_val
        if markup_type == 'Percentage':
            return (grand_total / 100) * markup_val

    def get_each_line_markup_division_amount(self, markup_amount):
        # find number of orderlines and add this amount also
        count = 0
        if markup_amount:
            # now check for
            if self.labor_ids:
                count += 1
            if self.material_ids:
                count += len(self.material_ids)
            if self.overhead_ids:
                count += len(self.overhead_ids)
            if self.internal_rental_ids:
                count += len(self.internal_rental_ids)
            if self.outsource_rental_ids:
                count+=len(self.outsource_rental_ids)
        if markup_amount > 0:
            return (markup_amount / count)
        else:
            return 0

    @api.depends('markup_type', 'markup_value', 'grand_total')
    def get_quotation_value(self):
        q_uotation_value = 0.0
        if self.grand_total:
            if not self.markup_value:
                q_uotation_value = self.grand_total
            else:
                q_uotation_value = self.get_markup_amount(self.grand_total, self.markup_type,
                                                          self.markup_value) + self.grand_total
        self.quotation_value = q_uotation_value

    @api.onchange('markup_type', 'markup_value', 'grand_total')
    def onchange_quotation_value(self):
        q_uotation_value = 0.0
        if self.grand_total:
            if not self.markup_value:
                q_uotation_value = self.grand_total
            else:
                q_uotation_value = self.get_markup_amount(self.grand_total, self.markup_type,
                                                          self.markup_value) + self.grand_total
        self.quotation_value = q_uotation_value

    def create_quotation(self):
        if self.state=='Approved':

            if len(self.material_ids) > 0 or len(self.internal_rental_ids) > 0 or len(self.overhead_ids) or len(self.labor_total) > 0 or len(self.outsource_rental_ids)>0:
                markup_amount_line = self.get_each_line_markup_division_amount(
                    self.get_markup_amount(self.grand_total, self.markup_type, self.markup_value))
                sale_order = self.env['sale.order'].create(
                    {'cost_sheet_id': self.id, 'partner_id': self.client.id,
                     'date_order': self.cost_sheet_date})
                if len(self.scope_work) > 0:
                    for obj in self.scope_work:
                        sale_order_line = self.env['scope.work.line'].create(
                            {'saleorder': sale_order.id, 'product_id': obj.product_id.id,
                             'name': obj.product_id.name,
                             'desc':obj.desc,
                             'total_qty': obj.total_qty, 'total_cost': obj.total_cost})
                if len(self.material_ids) > 0:
                    for obj in self.material_ids:
                        sale_order_line = self.env['sale.order.line'].create(
                            {'order_id': sale_order.id, 'product_id': obj.product_id.id,
                             'name': obj.product_id.name,
                             'product_uom_qty': obj.qty, 'price_unit': obj.rate + markup_amount_line})
                if len(self.internal_rental_ids) > 0:
                    for obj in self.internal_rental_ids:
                        sale_order_line = self.env['sale.order.line'].create(
                            {'order_id': sale_order.id, 'product_id': obj.product_id.id,
                             'name': obj.product_id.name,
                             'product_uom_qty': obj.qty, 'price_unit': obj.rate + markup_amount_line})
                if len(self.outsource_rental_ids) > 0:
                    for obj in self.outsource_rental_ids:
                        sale_order_line = self.env['sale.order.line'].create(
                            {'order_id': sale_order.id, 'product_id': obj.product_id.id,
                             'name': obj.product_id.name,
                             'product_uom_qty': obj.qty, 'price_unit': obj.rate + markup_amount_line})


                if len(self.overhead_ids) > 0:
                    for obj in self.overhead_ids:
                        sale_order_line = self.env['sale.order.line'].create(
                            {'order_id': sale_order.id, 'product_id': obj.product_id.id,
                             'name': obj.product_id.name,
                             'product_uom_qty': obj.qty, 'price_unit': obj.rate + markup_amount_line})
                if self.labor_total > 0:
                    # get product with name labor cost
                    product_labcost = self.env['product.product'].search([('name', '=', 'labor cost')])
                    if product_labcost:
                        sale_order_line = self.env['sale.order.line'].create(
                            {'order_id': sale_order.id, 'product_id': product_labcost.id,
                             'name': product_labcost.name,
                             'product_uom_qty': 1, 'price_unit': self.labor_total + markup_amount_line})

                self.is_quotation_generated = True
                self.quotation_count+=1
        else:
            raise ValidationError(
                    _("Please Approve the cost sheet by Manager"))

    @api.depends('material_total', 'labor_total', 'overhead_total', 'rental_total','rental_total_out')
    def grand_total_cal(self):
        for record in self:
            record.grand_total = record.material_total + record.labor_total + record.overhead_total + record.rental_total+record.rental_total_out

    @api.depends('material_ids')
    def material_total_cal(self):
        sum = 0
        if self.material_ids:
            for record in self.material_ids:
                if record.subtotal:
                    sum += record.subtotal
        self.material_total = sum

    @api.depends('labor_ids')
    def labor_total_cal(self):
        sum = 0
        if self.labor_ids:
            for record in self.labor_ids:
                if record.subtotal:
                    sum += record.subtotal
        self.labor_total = sum

    @api.depends('overhead_ids')
    def overhead_total_cal(self):
        sum = 0
        if self.overhead_ids:
            for record in self.overhead_ids:
                if record.subtotal:
                    sum += record.subtotal
        self.overhead_total = sum

    @api.depends('internal_rental_ids')
    def rental_total_cal(self):
        sum = 0
        if self.internal_rental_ids:
            for record in self.internal_rental_ids:
                if record.subtotal:
                    sum += record.subtotal
        self.rental_total = sum

    @api.depends('outsource_rental_ids')
    def rental_total_cal_out(self):
        sum = 0
        if self.outsource_rental_ids:
            for record in self.outsource_rental_ids:
                if record.subtotal:
                    sum += record.subtotal
        self.rental_total_out= sum





    @api.model
    def create(self, vals):
        is_add = self.env.context.get('is_additional')
        csr_id = self.env.context.get('default_parent_cost_sheet_ref')
        opertunity_id = self.env.context.get('default_opportunity_id')

        csr = self.env['cost.sheet.crm'].browse(csr_id)

        if is_add:
            csno = self.env['ir.sequence'].next_by_code('cstadd')
            vals['name'] = '19' + csno + 'A_CS'
            if csr.dafult_cost_sheet_ref:
                vals['dafult_cost_sheet_ref'] = csr.dafult_cost_sheet_ref.id
            else:
                vals['dafult_cost_sheet_ref'] = csr.id

            vals['opportunity_id'] = opertunity_id
            vals['is_additional'] = True
            vals['crm_lead']=csr.crm_lead.id
            vals['client']=csr.client.id


        else:
            csno = self.env['ir.sequence'].next_by_code('cst')
            vals['name'] = 'CS' + '19' + csno
            vals['is_additional'] = False
            # vals['opportunity_id']=

        # if csr:
        #     vals['dafult_cost_sheet_ref']=dcsr
        # else:
        #     vals['dafult_cost_sheet_ref']=self.id

        # if 'parent_cost_sheet_ref' in vals and vals['parent_cost_sheet_ref']:

        res = super(Costsheet, self).create(vals)
        return res

    # @api.model
    def final_total_cal(self):
        for sc in self.scope_work:
            sc.total_cost = 0.0

        for rec in self:
            for dta in rec:
                sum = 0
                qty=0
                mat_tot=0.0
                last_p=-1
                if dta.material_ids:
                    for sc in dta.scope_work:
                        last_p = -1
                        sum = 0
                        qty = 0
                        mat_tot=0.0
                        for mt in dta.material_ids:
                            if (sc.product_id.id == mt.product_final.id) or (len(mt.product_final)==0 and last_p > 0):
                                last_p=sc.product_id.id
                                sum += mt.subtotal
                                mat_tot+=mt.mat_purchase
                                qty+=mt.qty
                            else:
                                # sum = 0
                                # qty=0
                                last_p=-1
                        sc.total_cost += sum
                        sc.mat_pur_tot=mat_tot
                sum = 0
                qty = 0
                last_p = -1
                if dta.labor_ids:
                    for sc in dta.scope_work:
                        last_p = -1
                        sum = 0
                        qty = 0
                        for mt in dta.labor_ids:
                            if (sc.product_id.id == mt.product_final.id) or (len(mt.product_final) == 0 and last_p > 0):
                                last_p = sc.product_id.id
                                sum += mt.subtotal
                                qty += mt.qty
                            else:
                                # sum = 0
                                # qty = 0
                                last_p = -1
                        sc.total_cost += sum

                sum = 0
                qty = 0
                last_p = -1
                if dta.overhead_ids:
                    for sc in dta.scope_work:
                        last_p = -1
                        sum = 0
                        qty = 0
                        for mt in dta.overhead_ids:
                            if (sc.product_id.id == mt.product_final.id) or (len(mt.product_final) == 0 and last_p > 0):
                                last_p = sc.product_id.id
                                sum += mt.subtotal
                                qty += mt.qty
                            else:
                                # sum = 0
                                # qty = 0
                                last_p = -1
                        sc.total_cost += sum

                sum = 0
                qty = 0
                last_p = -1
                if dta.internal_rental_ids:
                    for sc in dta.scope_work:
                        last_p = -1
                        sum = 0
                        qty = 0
                        for mt in dta.internal_rental_ids:
                            if (sc.product_id.id == mt.product_final.id) or (len(mt.product_final) == 0 and last_p > 0):
                                last_p = sc.product_id.id
                                sum += mt.subtotal
                                qty += mt.qty
                            else:
                                # sum = 0
                                # qty = 0
                                last_p = -1
                        sc.total_cost += sum

                sum = 0
                qty = 0
                last_p = -1
                if dta.outsource_rental_ids:
                    for sc in dta.scope_work:
                        last_p = -1
                        sum = 0
                        qty = 0
                        for mt in dta.outsource_rental_ids:
                            if (sc.product_id.id == mt.product_final.id) or (len(mt.product_final) == 0 and last_p > 0):
                                last_p = sc.product_id.id
                                sum += mt.subtotal
                                qty += mt.qty
                            else:
                                # sum = 0
                                # qty = 0
                                last_p = -1
                        sc.total_cost += sum




class costsheetwcope(models.Model):
    _name = 'scope.work.line'

    saleorder = fields.Many2one('sale.order')
    name=fields.Char("name")
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'product'),('final_prod', '=', True)], string='Final Product',
                                 required=True)
    desc=fields.Char(string="Description")
    tax_id = fields.Many2one(
        'account.tax',
        index=True,
        string='Tax ID',
    )
    total_cost= fields.Float(string="total")
    total_qty=fields.Integer(string="Qty",store=True)


class costsheetwcope(models.Model):
    _name = 'scope.work'

    cost_sheet = fields.Many2one('cost.sheet.crm')
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'product'),('final_prod', '=', True)], string='Final Product', ondelete='cascade',
                                 required=True)
    desc=fields.Char(string="Description")

    total_cost= fields.Float(string="total")
    mat_pur_tot=fields.Float(string="Material Total")
    total_qty=fields.Integer(string="Qty",store=True,default=1)


class costsheetmaterial(models.Model):
    _name = 'cost.sheet.material'

    # domain = [('type', '=', 'product')]

    cost_sheet = fields.Many2one('cost.sheet.crm')
    # scope = fields.One2many(related='cost_sheet.scope_work')
    product_final = fields.Many2one('product.product', string='Final Product', domain=[('final_prod','=',True)],
                                 required=False,readonly=False,store=True,copy=True)
    product_id = fields.Many2one('product.product', domain=[('type', '=', 'product'),('raw_mat', '=', True)], string='Particular',
                                 required=True, ondelete='cascade')
    qty_ava = fields.Float(related='product_id.qty_available', string="Qty avaialble", store=True, readonly=True)
    qty = fields.Float(string='Qty.', default=1)
    uom = fields.Many2one('uom.uom', string='UOM')
    rate = fields.Float(string='Rate')
    subtotal = fields.Float(string='Total')
    department=fields.Many2one('hr.department',string='Department')
    days=fields.Char(string='Day(s)')
    hours=fields.Char(string='hour(s)')
    mat_purchase=fields.Float("Material Purchase")

    @api.onchange('product_final')
    def onchange_product_id(self):
        variant_ids_list = []
        result=[]
        if self._context.get('scope'):
            scop=self._context.get('scope')
            for rec in scop:
                cnt=0
                for pr in rec:
                    cnt+=1
                    if cnt==2 and pr:
                        scope = self.env["scope.work"].browse(pr)
                        if scope:
                           variant_ids_list.append(scope.product_id.id)

        return {'domain':{'product_final': [('id', 'in', variant_ids_list)]}}



    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.rate = self.product_id.lst_price

    @api.onchange('qty', 'rate')
    def onchange_products(self):
        if self.qty and self.rate:
            self.subtotal = self.qty * self.rate
        if self.product_id and self.qty:
            self.mat_purchase=self.product_id.standard_price * self.qty



class costsheetlabors(models.Model):
    _name = 'cost.sheet.labors'
    cost_sheet = fields.Many2one('cost.sheet.crm')

    scope = fields.Many2one('scope.work')
    product_final = fields.Many2one(related='scope.product_id', string='Final Product',copy=True,
                                    required=False, readonly=False, store=True)

    product_id = fields.Many2one('product.product', string='Particular', required=True, ondelete='cascade')

    job_id = fields.Many2one('hr.job', string='Designations', required=True)
    qty = fields.Float(string='Qty.', default=1)
    uom = fields.Many2one('uom.uom', string='UOM')
    rate = fields.Float(string='Rate')
    subtotal = fields.Float(string='Total')
    department=fields.Many2one('hr.department',string='Department')
    days=fields.Char(string='Day(s)')
    hours=fields.Char(string='hour(s)')

    @api.onchange('qty', 'rate')
    def onchange_product(self):
        if self.qty and self.rate:
            self.subtotal = self.qty * self.rate


    @api.onchange('product_final')
    def onchange_product_id(self):
        variant_ids_list = []
        result=[]
        if self._context.get('scope'):
            scop=self._context.get('scope')
            for rec in scop:
                cnt=0
                for pr in rec:
                    cnt+=1
                    if cnt==2 and pr:
                        scope = self.env["scope.work"].browse(pr)
                        if scope:
                           variant_ids_list.append(scope.product_id.id)

        return {'domain':{'product_final': [('id', 'in', variant_ids_list)]}}


class costsheetmaterial(models.Model):
    _name = 'cost.sheet.overhead'

    cost_sheet = fields.Many2one('cost.sheet.crm')
    scope = fields.Many2one('scope.work')
    product_final = fields.Many2one(related='scope.product_id', string='Final Product',copy=True,
                                    required=False, readonly=False, store=True)
    product_id = fields.Many2one('product.product', string='Particular', required=True, ondelete='cascade')
    qty = fields.Float(string='Qty.', default=1)
    uom = fields.Many2one('uom.uom', string='UOM')
    rate = fields.Float(string='Rate')
    subtotal = fields.Float(string='Total')

    department=fields.Many2one('hr.department',string='Department')
    days=fields.Char(string='Day(s)')
    hours=fields.Char(string='hour(s)')

    @api.onchange('qty', 'rate')
    def onchange_product(self):
        if self.qty and self.rate:
            self.subtotal = self.qty * self.rate


    @api.onchange('product_final')
    def onchange_product_id(self):
        variant_ids_list = []
        result=[]
        if self._context.get('scope'):
            scop=self._context.get('scope')
            for rec in scop:
                cnt=0
                for pr in rec:
                    cnt+=1
                    if cnt==2 and pr:
                        scope = self.env["scope.work"].browse(pr)
                        if scope:
                           variant_ids_list.append(scope.product_id.id)

        return {'domain':{'product_final': [('id', 'in', variant_ids_list)]}}


class costsheetmaterial(models.Model):
    _name = 'cost.sheet.rental.internal'

    cost_sheet = fields.Many2one('cost.sheet.crm')
    scope = fields.Many2one('scope.work')
    product_final = fields.Many2one(related='scope.product_id', string='Final Product',copy=True,
                                    required=False, readonly=False, store=True)
    product_id = fields.Many2one('product.product', string='Particular', required=True, ondelete='cascade')
    qty = fields.Float(string='Qty.', default=1)
    uom = fields.Many2one('uom.uom', string='UOM')
    rate = fields.Float(string='Rate')
    subtotal = fields.Float(string='Total')

    department=fields.Many2one('hr.department',string='Department')
    days=fields.Char(string='Day(s)')
    hours=fields.Char(string='hour(s)')

    @api.onchange('qty', 'rate')
    def onchange_product(self):
        if self.qty and self.rate:
            self.subtotal = self.qty * self.rate


    @api.onchange('product_final')
    def onchange_product_id(self):
        variant_ids_list = []
        result=[]
        if self._context.get('scope'):
            scop=self._context.get('scope')
            for rec in scop:
                cnt=0
                for pr in rec:
                    cnt+=1
                    if cnt==2 and pr:
                        scope = self.env["scope.work"].browse(pr)
                        if scope:
                           variant_ids_list.append(scope.product_id.id)

        return {'domain':{'product_final': [('id', 'in', variant_ids_list)]}}



class costsheetmaterial(models.Model):
    _name = 'cost.sheet.rental.outsource'

    cost_sheet = fields.Many2one('cost.sheet.crm')
    scope = fields.Many2one('scope.work')
    product_final = fields.Many2one(related='scope.product_id', string='Final Product',copy=True,
                                    required=False, readonly=False, store=True)
    product_id = fields.Many2one('product.product', string='Particular', required=True, ondelete='cascade')
    qty = fields.Float(string='Qty.', default=1)
    uom = fields.Many2one('uom.uom', string='UOM')
    rate = fields.Float(string='Rate')
    subtotal = fields.Float(string='Total')

    department=fields.Many2one('hr.department',string='Department')
    days=fields.Char(string='Day(s)')
    hours=fields.Char(string='hour(s)')

    @api.onchange('qty', 'rate')
    def onchange_product(self):
        if self.qty and self.rate:
            self.subtotal = self.qty * self.rate


    @api.onchange('product_final')
    def onchange_product_id(self):
        variant_ids_list = []
        result=[]
        if self._context.get('scope'):
            scop=self._context.get('scope')
            for rec in scop:
                cnt=0
                for pr in rec:
                    cnt+=1
                    if cnt==2 and pr:
                        scope = self.env["scope.work"].browse(pr)
                        if scope:
                           variant_ids_list.append(scope.product_id.id)

        return {'domain':{'product_final': [('id', 'in', variant_ids_list)]}}


class CRM(models.Model):
    _inherit = 'crm.lead'

    is_cost_sheet_generated = fields.Boolean(default=False,compute='check_cs_gen')
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=10, index=True,
                                 required=1,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    def check_cs_gen(self):
        cost_sheet = self.env['cost.sheet.crm'].search(
            [('crm_lead', '=', self.id), ('dafult_cost_sheet_ref', '=', False)], limit=1)
        if cost_sheet:
            self.is_cost_sheet_generated=True
        else:
            self.is_cost_sheet_generated=False


    def open_cost_sheet(self):

        # if record is there open else create it
        # project = self.env['project.project'].search([('name','=',self.name)],limit=1)

        cost_sheet = self.env['cost.sheet.crm'].search(
            [('crm_lead', '=', self.id), ('dafult_cost_sheet_ref', '=', False)], limit=1)
        if len(cost_sheet)>0:
            return {
                'name': _('Cost Sheet'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cost.sheet.crm',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': cost_sheet.id
            }
        else:
            # project = self.env['project.project'].create({'name': self.name})

            cost_sheet = self.env['cost.sheet.crm'].create({'crm_lead': self.id})
            if cost_sheet:
               self.is_cost_sheet_generated = True
               return {
                'name': _('Cost Sheet'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cost.sheet.crm',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': cost_sheet.id
                 }

    def generate_cost_sheet(self):
        # if record is there open else create it

        # project = self.env['project.project'].create({'name': self.name})

        cost_sheet = self.env['cost.sheet.crm'].create({'crm_lead': self.id,'client':self.partner_id.id,'crm_lead':self.id})
        if cost_sheet:
            self.is_cost_sheet_generated = True
            return {
                'name': _('Cost Sheet'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cost.sheet.crm',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': cost_sheet.id
            }


class saleorder(models.Model):
    _inherit = 'sale.order'
    cost_sheet_id = fields.Many2one('cost.sheet.crm')
    project = fields.Many2one('project.project', string='Project')
    is_allmaterial_availbile = fields.Boolean(default=False)

    scope_work = fields.One2many('scope.work.line', 'saleorder',store=True)


    def create_bom(self):
        view_id = self.env.ref('mrp.mrp_bom_form_view')
        bom_list = []
        if self.order_line and self.cost_sheet_id:
            for rec in self.order_line:
                if rec.product_id.id in self.cost_sheet_id.material_ids.product_id.ids:
                    bom_list.append([0, 0, {'product_id': rec.product_id.id, 'product_qty': rec.product_uom_qty,'product_uom_id':rec.product_uom.id

                                            }])
        return {
            'name': _('Bills of Material'),
            'view_id': view_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_bom_line_ids': bom_list,
            },
        }

    def process_material(self):
        # against costsheet
        material_notavailble_list = []
        if self.order_line and self.cost_sheet_id:
            for record in self.order_line:
                if record.product_id.id in self.cost_sheet_id.material_ids.product_id.ids:
                    if record.product_uom_qty > record.product_id.qty_available:
                        material_notavailble_dict = {}
                        material_notavailble_dict['product_id'] = record.product_id.id
                        material_notavailble_dict['qty'] = record.product_uom_qty - record.product_id.qty_available
                        material_notavailble_dict['uom'] = record.product_uom.id

                        material_notavailble_list.append(material_notavailble_dict)
            if material_notavailble_list:
                is_allmaterial_availbile = False

                requisition_list = []
                for rec in material_notavailble_list:
                    requisition_list.append(
                        [0, 0, {'product_id': rec['product_id'], 'date_planned': datetime.datetime.now().date(),
                                'product_uom': rec['uom'], 'name': rec['product_id'], 'product_qty': rec['qty']

                                }])

                view_id = self.env.ref('purchase.purchase_order_form')
                return {
                    'name': _('Purchase Requistion'),
                    'view_id': view_id.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'context': {
                        'default_order_line': requisition_list,
                    },
                }

            else:
                is_allmaterial_availbile = True

    def check_material_availbility(self, cost_sheet_obj):
        # against costsheet
        material_notavailble_name = []
        material_notavailble_list = []
        if self.order_line:
            for record in self.order_line:
                if record.product_id.id in cost_sheet_obj.material_ids.product_id.ids:
                    if record.product_uom_qty > record.product_id.qty_available:
                        material_notavailble_dict = {}
                        material_notavailble_dict['product_id'] = record.product_id.id
                        material_notavailble_name.append(record.product_id.name)
                        material_notavailble_dict['qty'] = record.product_uom_qty - record.product_id.qty_available
                        material_notavailble_list.append(material_notavailble_dict)
            if material_notavailble_list:
                self.is_allmaterial_availbile = False
                raise ValidationError(
                    _("Materials {0} not available create Purchase Requistion".format(material_notavailble_name)))

            else:
                self.write({'is_allmaterial_availbile': True})

    def action_confirm(self):
        res = super(saleorder, self).action_confirm()
        if self.cost_sheet_id:
            # self.check_material_availbility(self.cost_sheet_id)
            proj = self.env['project.project'].search([('name', '=', self.cost_sheet_id.opportunity_id.name)])
            self.write({'project': proj.id})
            # now update opportunity to won
            lead = self.env['crm.lead'].search([('name', '=', proj.name)], limit=1)
            if lead:
                lead.write(
                    {'stage_id': lead._stage_find(domain=[('is_won', '=', True)]).id})
        return res




            




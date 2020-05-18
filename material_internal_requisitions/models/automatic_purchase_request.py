from odoo import models,fields,api,_
from odoo.exceptions import UserError
import datetime


class procurement(models.Model):
    _name = 'requisition.procurement'
    
    name = fields.Char()
    product_id = fields.Many2one('product.product',string="Product")
    product_qty = fields.Float(string="Quantity")
    date = fields.Date(string="Date Requested")
    requisition_id = fields.Many2one('internal.requisition',string="Internal requisition")
    purchase_request_id = fields.Many2one('purchase.request',string="Purchase Request")
    purchase_agreement_id = fields.Many2one('purchase.requisition',string="Purchase Agreement")
    status = fields.Selection([('waiting','Waiting'),('in_progress','In Progress'),('done','Done')],default="waiting",string="Status")
    type = fields.Selection([('purchase_request','Purchase Request')],string="Type", default='purchase_request')
    

class wizard_create_purchase(models.TransientModel):
    _name = 'wizard.create.purchase'
    
    type = fields.Selection([('purchase_request','Purchase Request')])
    

    def create_purchase(self):
        records = self.env['requisition.procurement'].browse(self.env.context.get('active_ids'))
          
        if len(records.filtered(lambda x:x.status != 'waiting')) > 0:
            raise UserError(_('Selected Records should be in Waiting state'))
           
        if len(records.filtered(lambda x:x.status in ['in_progress','done'])) > 0:
            raise UserError(_('Wrong Selection,Purchase Request already created'))
        
        if self.type == 'purchase_request':   
            value = {'requested_by': self.env.uid,'origin':'IR','date_start': datetime.date.today()}
            PR = self.env['purchase.request'].create(value)
        
        if self.type =='purchase_agreement':
            value = {'user_id': self.env.uid,'origin':'IR'}
            PR = self.env['purchase.requisition'].create(value)
        
        if self.type == 'purchase_request':
            for rec in records:
                PR.line_ids.create({'product_id': rec.product_id.id,'product_qty': rec.product_qty,'request_id': PR.id})
                rec.write({'purchase_request_id':PR.id,'status':'in_progress','type':self.type})
        else:
            for rec in records:
                PR.line_ids.create({'product_id': rec.product_id.id,'product_qty': rec.product_qty,'requisition_id': PR.id})
                rec.write({'purchase_agreement_id':PR.id,'status':'in_progress','type':self.type})


class inherit_Purchase_request(models.Model):
    _inherit = 'purchase.request'


    def unlink(self):
        for rec in self:
            if rec.state == 'draft':
                self._cr.execute("update requisition_procurement set status='waiting' where purchase_request_id=%s" % (rec.id))

        return super(inherit_Purchase_request,self).unlink()

    def button_approved(self):
        res = super(inherit_Purchase_request, self).button_approved()
        self._cr.execute("update requisition_procurement set status='done' where purchase_request_id=%s" % (self.id))
        return res


class inherit_stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    purchase_request_done = fields.Boolean(default=False)
    
    def procure_requisition(self):
        
        if self.purchase_request_done:
            return 
        else:
            for rec in self.move_ids_without_package.filtered(lambda r:r.product_uom_qty != r.reserved_availability):
                diff = rec.product_uom_qty - rec.reserved_availability
                
                self.env['requisition.procurement'].create({'name':self.origin,'product_id':rec.product_id.id,'product_qty':diff,
                                                            'date':datetime.date.today(),'requisition_id':self.inter_requi_id.id})
                self.purchase_request_done = True
                

    def action_assign(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        # If a package level is done when confirmed its location can be different than where it will be reserved.
        # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
        package_level_done = self.mapped('package_level_ids').filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
        package_level_done.write({'is_done': False})
        moves._action_assign()
        package_level_done.write({'is_done': True})
        
        self.procure_requisition()
        return True
    

    def do_unreserve(self):
        records = self.env['requisition.procurement'].search([('requisition_id','=',self.inter_requi_id.id),('status','=','waiting')])
        
        for rec in records:
            rec.unlink()
            self.purchase_request_done = False
        
        return super(inherit_stock_picking,self).do_unreserve()
    
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class inherithremploye(models.Model):
    _inherit = 'product.template'


    name = fields.Char('Name', index=True, translate=True,default="-")

    p_type=fields.Many2one('product.type',string="Type")
    p_color=fields.Many2one('product.color',string="Color")

    p_length=fields.Many2one('product.length',string="Length")

    p_width=fields.Many2one('product.width',string="Width")
    p_height=fields.Many2one('product.height',string="Height")
    p_made=fields.Many2one('product.made',string="Made")

    brand= fields.Many2one('brand', string='Brand')
    raw_mat = fields.Boolean(string="Raw Material", default=False)
    final_prod = fields.Boolean(string="Final Product", default=False)
    overhead_mat = fields.Boolean(string="Overhead Materail", default=False)


    @api.model
    def create(self, vals):
        res = super(inherithremploye, self).create(vals)
        if res.raw_mat:
            res.name=""
            if res.categ_id.parent_id:
               names=res.categ_id.parent_id.name + ' ' + res.categ_id.name + ' '
            else:
                names = res.categ_id.name + ' '

            if res.p_length:
                names += res.p_length.name+' '
            if res.p_width:
                names += 'X' + res.p_width.name+' '
            if res.p_height:
                names += 'X' + res.p_height.name +' '

            names+= res.p_type.name  + ' ' + res.p_made.name + ' ' + res.brand.name
            res.name=str(names)

        return res

    def write(self, vals):
        if 'raw_mat' in vals:
            if vals['raw_mat'] == True:
                if self.categ_id.parent_id:
                    names = self.categ_id.parent_id.name + ' ' + self.categ_id.name + ' '
                else:
                    names = self.categ_id.name + ' '
                if self.p_length:
                   names +=  self.p_length.name+' '
                if self.p_width:
                    names += 'X' + self.p_width.name+' '
                if self.p_height:
                    names += 'X' +self.p_height.name+' '

                names+= ' '+ self.p_type.name  + ' ' + self.p_made.name + ' ' + self.brand.name
                vals['name']=str(names)
        rslt = super(inherithremploye, self).write(vals)
        return rslt








class brandclas(models.Model):
    _name = 'brand'

    name=fields.Char("Brand")



class product_types(models.Model):
    _name = 'product.type'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")



class product_color(models.Model):
    _name = 'product.color'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")




class product_length(models.Model):
    _name = 'product.length'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")




class product_width(models.Model):
    _name = 'product.width'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")





class product_height(models.Model):
    _name = 'product.height'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")


class product_made(models.Model):
    _name = 'product.made'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")


class emp_designation(models.Model):
    _name = 'employee.designation'
    _rec_name = 'designation'

    designation=fields.Char(string="Designation",required=1)
    rate=fields.Many2one('employee.rate',required=1)

class emp_designation_rate(models.Model):
    _name = 'employee.rate'
    _rec_name = 'rate'

    rate = fields.Float(string="Rate",required=1)
    desc = fields.Char(string="Description")








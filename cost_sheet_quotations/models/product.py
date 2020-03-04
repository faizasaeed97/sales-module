from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError


class Costsheet(models.Model):
    _inherit = 'product.template'

    raw_mat = fields.Boolean(string='Raw Material')
    final_prod = fields.Boolean(string='Final Product')
    product_size = fields.Char("size")
    product_color =  fields.Char("Color")

class prod_inheritx(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        result = []
        for record in self:
            if record.product_tmpl_id.name and record.product_tmpl_id.product_size:
               record_name = record.product_tmpl_id.name + ' - ' + record.product_tmpl_id.product_size
            else:
                record_name = record.product_tmpl_id.name

            result.append((record.id, record_name))
        return result





class account_projwork(models.Model):
    _inherit = 'account.account'

    def _set_opening_debit_credit(self, amount, field):
        """ Generic function called by both opening_debit and opening_credit's
        inverse function. 'Amount' parameter is the value to be set, and field
        either 'debit' or 'credit', depending on which one of these two fields
        got assigned.
        """
        opening_move = self.company_id.account_opening_move_id

        if not opening_move:
            raise UserError(_("You must first define an opening move."))

        if opening_move.state in ['posted','cancel','draft']:
            # check whether we should create a new move line or modify an existing one
            opening_move_line = self.env['account.move.line'].search([('account_id', '=', self.id),
                                                                      ('move_id','=', opening_move.id),
                                                                      (field,'!=', False),
                                                                      (field,'!=', 0.0)]) # 0.0 condition important for import

            counter_part_map = {'debit': opening_move_line.credit, 'credit': opening_move_line.debit}
            # No typo here! We want the credit value when treating debit and debit value when treating credit

            if opening_move_line:
                if amount:
                    # modify the line
                    opening_move_line.with_context(check_move_validity=False)[field] = amount
                elif counter_part_map[field]:
                    # delete the line (no need to keep a line with value = 0)
                    opening_move_line.with_context(check_move_validity=False).unlink()
            elif amount:
                # create a new line, as none existed before
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': _('Opening balance'),
                        field: amount,
                        'move_id': opening_move.id,
                        'account_id': self.id,
                })

            # Then, we automatically balance the opening move, to make sure it stays valid
            if not 'import_file' in self.env.context:
                # When importing a file, avoid recomputing the opening move for each account and do it at the end, for better performances
                self.company_id._auto_balance_opening_move()




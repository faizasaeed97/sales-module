#-*- coding: utf-8 -*-


from odoo import api, fields, models, _, SUPERUSER_ID




class cswizrdtr(models.TransientModel):
    _name = "wizard.cs.order"

    def print_btn(self):
        active_record = self._context['active_id']

        data = {
            'ids': self.ids,
            'cs_id':active_record,
            'model': self._name,
            # 'current_task':task_list
        }
        return self.env.ref('cost_sheet_quotations.action_repair_order_print').report_action(self, data=data)









# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expiry_notification_days = fields.Char(string="Expiry Notification Days", config_parameter="hr_base.expiry_notification_days")

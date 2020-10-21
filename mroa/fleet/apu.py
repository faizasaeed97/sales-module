from odoo import api, fields, models, _

class MROAProductTemplate(models.Model):
    _name = 'mroa.fleet.engines.apu'

    name = fields.Char("APU Serial Number")
    manufacture_date = fields.Date("APU Date Of Manufacturing")
    first_use_date = fields.Date("APU Date Of First Use")
    time_since_new = fields.Integer("Time Since New")
    total_apu_starts = fields.Integer("Total APU Starts")
    calendar_total_life_years = fields.Integer("Calendar Total Life")
    calendar_total_life_months = fields.Integer("Total APU Starts")
    total_apu_starts = fields.Integer("Total APU Starts")
    time_last_overhaul = fields.Integer("Time Since Last Overhaul")
    last_calendar_total_life_years = fields.Integer("Calendar Life Since Last Overhaul")
    last_calendar_total_life_months = fields.Integer("Total APU Starts")
    last_total_apu_starts = fields.Integer("APU Starts Since Last Overhaul")
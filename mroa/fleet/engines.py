from odoo import api, fields, models, _

class MROAProductTemplate(models.Model):
    _name = 'mroa.fleet.engines'

    name = fields.Char("Engine Serial Number", required=True)
    manufacturing_date = fields.Date("Manufacturing Date")
    first_use_date = fields.Date("First Use Date")
    time_since_new = fields.Integer("Time Since New")
    calendar_total_life_hours = fields.Char("Calendar Total Life")
    calendar_total_life_months = fields.Char("Calendar Total Life")
    total_engine_cycles = fields.Integer("Total Engine Cycles")
    time_since_last_overhaul = fields.Integer("Time Since Last OverHaul")
    calendar_life_last_overhaul_hour = fields.Integer("Calendar Life Since Last OverHaul")
    calendar_life_last_overhaul_month = fields.Integer("Calendar Life Since Last OverHaul")
    engine_cycle_life_last_overhaul_hour = fields.Integer("Engine Cycles Since Last OverHaul")
    engine_cycle_life_last_overhaul_month = fields.Integer("Total Engine Cycles")

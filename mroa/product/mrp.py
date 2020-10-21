from odoo import api, fields, models, _


class mrp_production_inherit(models.Model):
    _inherit = 'mrp.bom'

    bom_type = fields.Selection(
        [('Mandatory items', 'Mandatory items'), ('condition change items', 'condition change items')], string="Type")


class mrp_manuorder_inherit(models.Model):
    _inherit = 'mrp.production'

    Unit = fields.Char("unit")
    Reason = fields.Char("Reason")
    Manufacturer = fields.Char("Manufacturer")
    Manufacturing = fields.Char("Manufacturing")
    inspection_manufacturing_date = fields.Date("Manufacturing Date")

    Removed_from_Helicopter = fields.Many2one("mroa.fleet.vehicle", "Removed From Helicopter - Registration")
    Time_Sine_New = fields.Char("Time Sine New")
    Time_Since_Overhaul = fields.Char("Time Since Overhaul")
    calendar_life_months = fields.Integer("Calendar Life")
    calendar_life_years = fields.Integer("Calendar Life")
    Last_Repair_At = fields.Char("Last Repair At")
    Last_Repair_Date = fields.Date("Last Repair Date")
    Shop_Name = fields.Char(string="Shop name")

    aircraft_fleet = fields.Many2one("mroa.fleet.vehicle", string="Aircraft Fleet")

    @api.onchange('aircraft_fleet')
    def mroa_aircraft_fleet_onchng(self):
        if self.aircraft_fleet:
            rec = self.aircraft_fleet
            self.Time_Sine_New = rec.time_since_new
            self.Time_Since_Overhaul = rec.time_since_last_overhaul


class MrpWorkorder_inheritsx(models.Model):
    _inherit = 'mrp.workorder'

    inspection_unit = fields.Char("Unit")
    inspection_reason = fields.Char("Reason For Repair")
    inspection_manufacturer = fields.Char("Manufacturer")
    inspection_manufacturing_date = fields.Date("Manufacturing Date")
    removed_heli = fields.Many2one("mroa.fleet.vehicle", "Removed From Helicopter - Registration")

    calendar_life_months = fields.Integer("Calendar Life")
    calendar_life_years = fields.Integer("Calendar Life")
    starts_number = fields.Integer("Number Of Starts")
    airbleeds_number = fields.Integer("Number of Airbleeds")

    tsn = fields.Integer("TSN")
    tso = fields.Integer("TSO")
    total_repairs = fields.Integer("Total Repairs")
    last_repair_at = fields.Char("Last Repair At")
    last_repair_date = fields.Date("Last Repair Date")























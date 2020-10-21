from odoo import api, fields, models, _

class ConfigurationManagement(models.Model):
    _name = "mroa.fleet.configuration.mng"

    aircraft_type = fields.Many2many("fleet.vehicle.model", string="Aircraft Type")
    book_reference = fields.Char("Book Reference")
    aricraft_systems = fields.One2many("mroa.fleet.configuration.mng.systems", "conf_id",string="Systems of Aircraft")

class ConfigurationManagementSystemsSelection(models.Model):
    _name = "mroa.fleet.configuration.mng.systems"

    system_selection = fields.Many2one("mroa.system.required", string="Select System")
    qty = fields.Integer("Quantity", required=True)
    criticallity = fields.Many2one("mroa.configuration.critcality",string="Criticallity")
    obsolescence = fields.Many2one("mroa.configuration.obsolescence", string="Obsolescence")
    obsolescence_ref = fields.Char("Obsolescence Reference")
    obsolescence_ref_doc = fields.Binary("Reference Documents")
    llc_repairable = fields.Many2one("mroa.repairable.llc", string="Life Name")
    if_overhaul = fields.Boolean("If Overhauled")
    overhaul_life_value = fields.Float("Overhaul Life")
    slife_since_new = fields.Char("Service Life Since New")
    service_life_emergency_one = fields.Char("Service Life For Emergency 1")
    service_life_emergency_two = fields.Char("Service Life For Emergency 2")
    service_life_continous_operation = fields.Char("Sevice Life For Continuous Operations")
    service_life_years = fields.Char("Calander Life Years and Months")
    service_life_months = fields.Char("Calander Life Years and Months")
    cycle_since_new_one = fields.Integer("Cycles1 Since New")
    cycle_since_new_two = fields.Integer("Cycles2 Since New")
    cycle_since_new_three = fields.Integer("Cycles3 Since New")
    cycle_since_new_four = fields.Integer("Cycles4 Since New")
    cycle_since_new_five = fields.Integer("Cycles5 Since New")
    conf_id = fields.Many2one("mroa.fleet.configuration.mng", string="Confugration ID")

class MroaConfigurationCritical(models.Model):
    _name = "mroa.configuration.critcality"

    name = fields.Char("Name")

class MroaConfigurationObsolescence(models.Model):
    _name = "mroa.configuration.obsolescence"

    name = fields.Char("Name")

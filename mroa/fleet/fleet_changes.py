from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class MROAFleet(models.Model):
	_inherit = "fleet.vehicle"

	@api.depends('model_id.brand_id.name', 'model_id.nomenclature_name', 'license_plate')
	def _compute_vehicle_name(self):
		for record in self:
			record.name = (record.model_id.brand_id.name or '') + '/' + (record.license_plate or '')

	odometer_unit = fields.Selection([('kilometers', 'Kilometers'),('miles', 'Miles'),('hours', 'Hours')],
									 'Flying Meter Unit', default='hours', help='Unit of the Flying Meter', required=True)

	license_plate = fields.Char(tracking=True,
								help='License plate number of the Aircraft (i = plate number for a car)')
	vin_sn = fields.Char('Chassis Number', help='Unique number written on the Aircraft motor (VIN/SN number)',
						 copy=False)
	driver_id = fields.Many2one('res.partner', 'Driver', tracking=True, help='Driver of the Aircraft', copy=False)
	future_driver_id = fields.Many2one('res.partner', 'Future Driver', tracking=True, help='Next Driver of the Aircraft',
									   copy=False,
									   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
	model_id = fields.Many2one('fleet.vehicle.model', 'Model',
							   tracking=True, required=True, help='Model of the Aircraft')

	acquisition_date = fields.Date('Immatriculation Date', required=False,
								   default=fields.Date.today, help='Date when the Aircraft has been immatriculated')
	first_contract_date = fields.Date(string="First Contract Date", default=fields.Date.today)
	color = fields.Char(help='Color of the Aircraft')

	location = fields.Char(help='Location of the Aircraft (garage, ...)')
	seats = fields.Integer('Seats Number', help='Number of seats of the Aircraft')
	model_year = fields.Char('Model Year', help='Year of the model')
	doors = fields.Integer('Doors Number', help='Number of doors of the Aircraft', default=5)

	odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer', string='Last Odometer',
							help='Odometer measure of the Aircraft at the moment of this log')

	transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission',
									help='Transmission Used by the Aircraft')
	fuel_type = fields.Selection([
		('gasoline', 'Gasoline'),
		('diesel', 'Diesel'),
		('lpg', 'LPG'),
		('electric', 'Electric'),
		('hybrid', 'Hybrid')
	], 'Fuel Type', help='Fuel Used by the Aircraft')

	power = fields.Integer('Power', help='Power in kW of the Aircraft')
	co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the Aircraft')

class MROAFleetVehicle(models.Model):
	_inherits = {'fleet.vehicle': 'vehicle_id'}
	_name = 'mroa.fleet.vehicle'
	_description = 'Aircraft Fleet'

	def _get_odometer(self):
		FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
		for record in self:
			vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.vehicle_id.id)], limit=1, order='value desc')
			if vehicle_odometer:
				record.odometer = vehicle_odometer.value
			else:
				record.odometer = 0

	def _compute_count_all(self):
		Odometer = self.env['fleet.vehicle.odometer']
		LogFuel = self.env['fleet.vehicle.log.fuel']
		LogService = self.env['fleet.vehicle.log.services']
		LogContract = self.env['fleet.vehicle.log.contract']
		Cost = self.env['fleet.vehicle.cost']
		for record in self:
			record.odometer_count = Odometer.search_count([('vehicle_id', '=', record.vehicle_id.id)])
			record.fuel_logs_count = LogFuel.search_count([('vehicle_id', '=', record.vehicle_id.id)])
			record.service_count = LogService.search_count([('vehicle_id', '=', record.vehicle_id.id)])
			record.contract_count = LogContract.search_count([('vehicle_id', '=', record.vehicle_id.id), ('state', '!=', 'closed')])
			record.cost_count = Cost.search_count([('vehicle_id', '=', record.vehicle_id.id), ('parent_id', '=', False)])
			record.history_count = self.env['fleet.vehicle.assignation.log'].search_count(
				[('aircraft_id', '=', record.id)])

	def open_assignation_logs(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Assignation Logs',
			'view_mode': 'tree',
			'res_model': 'fleet.vehicle.assignation.log',
			'domain': [('vehicle_id', '=', self.vehicle_id.id)],
			'context': {'default_driver_id': self.driver_id.id, 'default_aircraft_id': self.id}
			}

	def act_show_log_cost(self):
		self.ensure_one()
		copy_context = dict(self.env.context)
		copy_context.pop('group_by', None)
		res = self.env['ir.actions.act_window'].for_xml_id('fleet', 'fleet_vehicle_costs_action')
		res.update(context=dict(copy_context, default_aircraft_id=self.id, search_default_parent_false=True),
			domain=[('vehicle_id', '=', self.vehicle_id.id),('aircraft_id', '=', self.id)])
		return res

	def return_action_to_open(self):
		""" This opens the xml view specified in xml_id for the current vehicle """
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('fleet', xml_id)
			res.update(context=dict(self.env.context, default_aircraft_id=self.id, group_by=False),domain=[('vehicle_id', '=', self.vehicle_id.id),('aircraft_id', '=', self.id)])
			return res
		return False

	def mroa_return_action_to_open(self):
		""" This opens the xml view specified in xml_id for the current vehicle """
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('fleet', xml_id)
			res.update(context=dict(self.env.context, default_aircraft_id=self.id, group_by=False),domain=[('vehicle_id', '=', self.vehicle_id.id),('aircraft_id', '=', self.id)])
			return res
		return False

	@api.depends('aircraft_name', 'license_plate')
	def _compute_vehicle_name(self):
		for record in self:
			if record.license_plate or record.aircraft_name:
				get = ""
				anget = ""
				if record.license_plate:
					get = "["+record.license_plate+"]"
				if record.aircraft_name:
					anget = record.aircraft_name.name
				record.name = get + " " + anget
			else:
				record.name = ''

	@api.depends('manufacture_date')
	def compute_calendar_total_life_hours(self):
		if self.manufacture_date:
			years = relativedelta(fields.Date.today(), self.manufacture_date).years
			self.calendar_total_life_hours = years
		else:
			self.calendar_total_life_hours = "0"

	@api.depends('last_overhaul_date')
	def compute_calendar_life_last_overhaul_hour(self):
		if self.last_overhaul_date:
			years = relativedelta(fields.Date.today(), self.last_overhaul_date).years
			self.calendar_life_last_overhaul_hour = years
		else:
			self.calendar_life_last_overhaul_hour = 0

	@api.depends('manufacture_date')
	def compute_calendar_total_life_months(self):
		if self.manufacture_date:
			differ = relativedelta(fields.Date.today(), self.manufacture_date).months
			self.calendar_total_life_months = differ
		else:
			self.calendar_total_life_months = "0"

	@api.depends('last_overhaul_date')
	def compute_calendar_life_last_overhaul_month(self):
		if self.last_overhaul_date:
			differ = relativedelta(fields.Date.today(), self.last_overhaul_date).months
			self.calendar_life_last_overhaul_month = differ
		else:
			self.calendar_life_last_overhaul_month = 0

	def compute_time_since_new(self):
		for record in self:
			if record.id:
				counter = 0
				values = self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',record.vehicle_id.id)])
				if values:
					for val in values:
						counter = counter + val.value

				record.time_since_new = counter

	@api.onchange('acquisition_date','manufacture_date')
	def onchange_manufacturing_acquisation_date(self):
		if self.acquisition_date and self.manufacture_date:
			if self.manufacture_date >= self.acquisition_date:
				raise ValidationError("Acquisation Date can not be greater than Manufacturing date")

	aircraft_name = fields.Many2one("mroa.aircraft.names",string="Aircraft Name", readonly=False)
	group_system = fields.Many2one("mroa.system.groups", string="Systems Group")
	group_statuses = fields.Many2one("mroa.system.status", string="Systems")
	assembly_id = fields.Many2many("product.template", string="Installed Assemblies")
	engines_id = fields.Many2many("mroa.fleet.engines", string="AirCraft Engines")
	apus_id = fields.Many2many("mroa.fleet.engines.apu", string="AirCraft APU")
	manufacture_date = fields.Date("Manufacturing Date")
	time_since_new = fields.Integer("Time Since New (TSN)", compute='compute_time_since_new')
	landing_numbers = fields.Integer("Landings Since New")
	time_since_last_overhaul = fields.Integer("Time Since Overhaul (TSO)")
	landings_last_overhaul = fields.Integer("No Of Landings Since OverHaul")
	calendar_total_life_hours = fields.Char("Calender Life Since New", compute='compute_calendar_total_life_hours')
	calendar_total_life_months = fields.Char("Calender Life Since New", compute='compute_calendar_total_life_months')
	calendar_life_last_overhaul_hour = fields.Integer("Calendar Life Since Overhaul", compute='compute_calendar_life_last_overhaul_hour')
	calendar_life_last_overhaul_month = fields.Integer("Calendar Life Since Overhaul", compute='compute_calendar_life_last_overhaul_month')
	aircraft_owner = fields.Char("Owner Of The Aircraft")
	maintain_workshop = fields.Char("Maintaining Workshop")
	concerned_depot = fields.Char("Concerned Depot")
	mode_induction = fields.Many2one("mroa.aircraft.mode.induction", string="Mode Of Induction")
	last_overhaul_date = fields.Date("Date Of Last Overhaul")
	service_life_last_verhaul = fields.Integer("Service Life at Last Overhaul")
	last_overhaul_workshop = fields.Char("Workshop Of Last Overhaul")
	date_last_overhaul_workshop = fields.Date("Date of Last Visit Of Aircraft to Workshop")
	purpose_visit_workshop = fields.Char("Purpose of Last Visit to Workshop")
	vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle ID", required=True)

class MROAFleetSystemGroups(models.Model):
	_name = "mroa.system.groups"

	name = fields.Char("Name")

class MROAFleetSystemRequired(models.Model):
	_name = "mroa.system.required"

	name = fields.Char("Name", required=True)
	vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle ID")

class MroaAircraftTypes(models.Model):
	_name = "mroa.aircraft.types"

	name = fields.Char("Name")

class MroaAircraftNames(models.Model):
	_name = "mroa.aircraft.names"

	name = fields.Char("Name")

class MroaAircraftCategories(models.Model):
	_name = "mroa.aircraft.categories"

	name = fields.Char("Name")

class MroaAircraftModeInduction(models.Model):
	_name = "mroa.aircraft.mode.induction"

	name = fields.Char("Name")

class MroaFleetVehicleModel(models.Model):
	_inherit = 'fleet.vehicle.model'

	@api.depends('name', 'brand_id')
	def name_get(self):
		res = []
		for record in self:
			name = record.nomenclature_name
			if record.brand_id.name:
				name = record.brand_id.name + '/' + (name.name or '')
			res.append((record.id, name))
		return res

	name = fields.Char('Model name', required=False)
	nomenclature_name = fields.Many2one('mroa.aircraft.names', string="Nomenclature Of Aircraft", required=True)
	aircraft_alias = fields.Char("Alias Of the Aircraft")
	manufacture_origin = fields.Many2one("res.country", string="Origin Of the Manufacturer")
	aircraft_model = fields.Char("Model")
	oem = fields.Char("Original Equipment Manufacturer")
	part_numbers = fields.Char(string="Part Numbers")
	aircraft_type = fields.Many2one("mroa.aircraft.types", string="Aircraft Types")
	aircraft_category = fields.Many2one("mroa.aircraft.categories", string="Aircraft Category")
	total_service_life = fields.Integer("Total Service Life")
	total_calendar_life_months = fields.Integer("Total Calendar Life")
	total_calendar_life_years = fields.Integer("Total Calendar Life")
	total_landing_numbers = fields.Integer("Total Number Of Landings")
	overhaul_service_life = fields.Integer("Overhaul Service Life")
	overhaul_calendar_life_years = fields.Integer("Overhaul Calendar Life")
	overhaul_calendar_life_months = fields.Integer("Overhaul Calendar Life")
	overhaul_landing_numbers = fields.Integer("Overhaul Number Of Landings")

class MroaFleetVehicleOdometer(models.Model):
	_inherit = 'fleet.vehicle.odometer'

	@api.onchange('aircraft_id')
	def onchange_aircraft_id(self):
		if self.aircraft_id:
			if self.aircraft_id.vehicle_id:
				self.vehicle_id = self.aircraft_id.vehicle_id.id

	@api.depends('value')
	def get_total_hours(self):
		for record in self:
			tot_hour=0
			if record.id:
				recs = self.env['fleet.vehicle.odometer'].search([('vehicle_id','!=',record.aircraft_id.id),('id','!=',record.id)])
				if recs:
					for rec in recs:
						tot_hour += rec.flying_hours

			record.total_Hours = tot_hour

	aircraft_id = fields.Many2one("mroa.fleet.vehicle", string="Aircraft")
	number_landings = fields.Integer("Number Of Landings")
	starts_number = fields.Integer("Number Of Starts")
	Faults_in_Flying = fields.Many2many('flying.faults',string="Faults in flying")
	Fault_Rectification = fields.Text(string="Fault Rectification")
	Spares_Used = fields.One2many('spares.used','fleet_spares',string="Spares Used")
	expendables_Used = fields.Many2many('expandable.used',string="Expendables Used")
	flying_hours = fields.Integer(string="Flying hours")
	total_Hours = fields.Integer(string="Total hours",compute='get_total_hours')


class Mroaflying_new(models.Model):
	_name = "flying.faults"

	name = fields.Char("Name")


class Mroasparesnew(models.Model):
	_name = "spares.used"

	name = fields.Many2one('product.template')
	qty=fields.Float(related='name.qty_available')
	fleet_spares = fields.Many2one('fleet.vehicle.odometer')


class Mroaexpandablenew(models.Model):
	_name = "expandable.used"

	name = fields.Char("Name")



class MroaLLCRepairableLife(models.Model):
	_name = "mroa.repairable.llc"

	name = fields.Char("Life Name")
	life_unit = fields.Many2one("uom.uom", string="Life Unit")
	life_value = fields.Float("Life Value")

class MROAFleetVehicleLogContract(models.Model):
	_inherit = 'fleet.vehicle.log.contract'

	@api.onchange('aircraft_id')
	def onchange_aircraft_id(self):
		if self.aircraft_id:
			if self.aircraft_id.vehicle_id:
				self.vehicle_id = self.aircraft_id.vehicle_id.id

	aircraft_id = fields.Many2one("mroa.fleet.vehicle", string="Aircraft")

class MROAFleetVehicleCost(models.Model):
	_inherit = 'fleet.vehicle.cost'

	@api.onchange('aircraft_id')
	def onchange_aircraft_id(self):
		if self.aircraft_id:
			if self.aircraft_id.vehicle_id:
				self.vehicle_id = self.aircraft_id.vehicle_id.id

	aircraft_id = fields.Many2one("mroa.fleet.vehicle", string="Aircraft")

class MROAFleetVehicleLogServices(models.Model):
	_inherit = 'fleet.vehicle.log.services'

	@api.onchange('aircraft_id')
	def onchange_aircraft_id(self):
		if self.aircraft_id:
			if self.aircraft_id.vehicle_id:
				self.vehicle_id = self.aircraft_id.vehicle_id.id

	aircraft_id = fields.Many2one("mroa.fleet.vehicle", string="Aircraft")

class MROAFleetVehicleLogFuel(models.Model):
	_inherit = 'fleet.vehicle.log.fuel'

	@api.onchange('aircraft_id')
	def onchange_aircraft_id(self):
		if self.aircraft_id:
			if self.aircraft_id.vehicle_id:
				self.vehicle_id = self.aircraft_id.vehicle_id.id

	aircraft_id = fields.Many2one("mroa.fleet.vehicle", string="Aircraft")
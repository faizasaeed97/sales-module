from odoo import api, fields, models, _

class MROAProductTemplate(models.Model):
    _inherit = 'product.template'

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'tail_reference'])
        return [(template.id, '%s%s' % (template.name, template.tail_reference and '[%s] ' % template.tail_reference or ''))
                for template in self]

    @api.depends('repair_condition')
    def compute_repair_condition_value(self):
        for record in self:
            if record.repair_condition:
                if 'Rotable' in record.repair_condition.name:
                    record.repair_condition_value = "Show"
                else:
                    record.repair_condition_value = "NoShow"
            else:
                record.repair_condition_value = "Show"

    @api.depends('required_ref','part_number','alter_part_number','nsn_number','manufacturer_number')
    def compute_header_number_show(self):
        for record in self:
            if record.required_ref:
                body_html = ""
                f_name = ""
                if record.required_ref == 'Part Number':
                    body_html = "<strong>Part Number:</strong>"
                    f_name = "Part Number: "
                    if record.part_number:
                        body_html += " <span>" + record.part_number + "</span>"
                        f_name += record.part_number
                elif record.required_ref == 'National Stock Number':
                    body_html = "<strong>National Stock Number:</strong>"
                    f_name = "National Stock Number: "
                    if record.nsn_number:
                        body_html += " <span>" + record.nsn_number + "</span>"
                        f_name += record.nsn_number
                elif record.required_ref == 'Manufacturer Number':
                    body_html = "<strong>Manufacturer Number:</strong>"
                    f_name = "Manufacturer Number: "
                    if record.manufacturer_number:
                        body_html += " <span>" + record.manufacturer_number + "</span>"
                        f_name += record.manufacturer_number
                elif record.required_ref == 'Alternate Part Number':
                    body_html = "<strong>Alternate Part Number:</strong>"
                    f_name = "Alternate Part Number: "
                    if record.alter_part_number:
                        body_html += " <span>" + record.alter_part_number + "</span>"
                        f_name += record.alter_part_number

                record.header_number_show = body_html
                record.tail_reference = f_name
            else:
                record.header_number_show = ""
                record.tail_reference = ""

    @api.onchange('aircraft_type')
    def onchange_aircraft_type(self):
        if self.aircraft_type:
            result = self.env['fleet.vehicle.model'].search([('aircraft_type','=', self.aircraft_type.id)])
            if result:
                an_result = self.env['mroa.fleet.vehicle'].search([('model_id', 'in', result.ids)])
                if an_result:
                    return {'domain': {'tail_number': [('id', 'in', an_result.ids)]}}

    is_assembly = fields.Boolean("Is Assembly")
    serial_number = fields.Char("Serial Number")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Aircraft ID")
    part_number = fields.Char("Part Number")
    alter_part_number = fields.Char("Alternate Part Number")
    nsn_number = fields.Char("National Stock Number")
    manufacturer_number = fields.Char("Manufecturer Number")
    alias = fields.Char("Alias")
    required_ref = fields.Selection([("Part Number","Part Number"),("National Stock Number","National Stock Number"),("Manufacturer Number","Manufacturer Number"),
                                     ('Alternate Part Number','Alternate Part Number')],
                                    string="Required Reference", help="Select Which Reference Number to Enter")
    header_number_show = fields.Html("Hello", compute="compute_header_number_show")
    can_purchase_locally = fields.Boolean("Can be Purchased Locally")
    can_make_order = fields.Boolean("Make to Order")
    manufacturer_name = fields.Char("Manufecturer Name")
    #relation_code = fields.Char(string="Relationship Code")
    relation_code = fields.Many2one("mroa.product.relation.code", string="Relationship Code")
    #serviceability = fields.Char(string="Serviceability")
    serviceability = fields.Many2one("mroa.product.service.code", string="Serviceability")
    cross_reference = fields.Many2many("product.product", string="Cross Reference")
    repair_condition = fields.Many2one("mroa.repair.condition.model", string="Repair Condition")
    repair_condition_value = fields.Char(string="Repair Code Value", compute="compute_repair_condition_value")
    repairable_llc = fields.Char("For Repairable and LLC-Repairable")
    repair_Code = fields.One2many("mroa.repair.code.model", "p_id", string="Repair Code")
    select_mroa = fields.One2many("mroa.repair.product.workshop", "p_id", string= "MRO")
    #trade_code = fields.Char(string="Trade Code")
    trade_code = fields.Many2one("mroa.product.trade.code", string="Trade Code")
    tools_testbenches = fields.One2many('tools.testbenches', 'tools_id', string="Tools Testbenches")
    type_prod = fields.Many2one('type.consumeable.model', string="Type")
    sparts_type_prod = fields.Many2one('type.spart.model', string="Type")
    expand_type_prod = fields.Many2one('type.expendable.model', string="Type")
    specification_prod = fields.One2many('specification.prod.models', 'con_prod_tmp_id', string="Specification")
    spart_specification_prod = fields.One2many('specification.prod.models', 'spart_prod_tmp_id',string="Specification")
    expand_specification_prod = fields.One2many('specification.prod.models', 'expand_prod_tmp_id', string="Specification")
    specification_unit = fields.Many2one('uom.uom', string="Specification Unit")
    spart_manufacturer_multiple_selection = fields.One2many('local.manufacturer', 'p_id', string="Manufacturers")
    expand_manufacturer_multiple_selection = fields.One2many('local.manufacturer', 'p_id', string="Manufacturers")
    local_manufacturer_multiple_selection = fields.One2many('local.manufacturer', 'p_id', string="Local manufacturer")
    local_vendors_multiple_selection = fields.One2many('local.manufacturer', 'p_id', string="Local Vendors")

    aircraft_type = fields.Many2one("mroa.aircraft.types", string="Aircraft Types")
    tail_number = fields.Many2one("mroa.fleet.vehicle",string="Tail Number")
    tbo_expendables_serial_number = fields.Many2one('product.tbo.serial.number', string="LLC Expendables Serial Number")
    purchase_year = fields.Char("Year Of Purchase", compute="compute_purchase_year")
    manufacture_date = fields.Date("Date Of Manufecture")
    date_induction_purchase = fields.Date("Date Of Induction or Purchase")
    date_last_visit_workshop_depot = fields.Date("Date Of Last Visit to Workshop OR Depot")
    last_visit = fields.Char("Last Visit Report")
    installation_date = fields.Date("Date Of Installation")
    removal_date = fields.Date("Date Of Removal")
    removal_reason = fields.Many2one("tail.product.removal.reason",string="Removal Reason")
    fault_details_authority = fields.Char("Fault Detail OR Control Exchange Authority")
    specific_type = fields.Selection([('Standard Parts', 'Standard Parts'),('Tools, Testbenches, GSE', 'Tools, Testbenches, GSE'),
                                           ('Expendables','Expendables')], string="Specific Type")

    currency = fields.Many2one("res.currency", string="Currency")
    tail_reference = fields.Char("Internal Reference")
    forecasting_ids = fields.One2many("product.forcasting.lsp", 'p_temp_id', string="Product Forecating")
    tail_internal_reference = fields.Char("Internal Reference")

class MroaProductRepairWorkShop(models.Model):
    _name = "mroa.repair.product.workshop"

    name = fields.Char("Name")
    p_id = fields.Many2one("product.template", string="Product ID")

class MroaRepairCodeModel(models.Model):
    _name = "mroa.repair.code.model"

    name = fields.Char("Name")
    p_id = fields.Many2one("product.template", string="Product ID")

class tools_testbenches_gse (models.Model):
    _name = 'tools.testbenches'

    @api.depends('TTG')
    def compute_what_ttg(self):
        for record in self:
            if record.TTG:
                record.what_ttg = record.TTG.name
                if record.TTG.name == "General Tools":
                    record.measuring_value = False
                    record.measurement_ranges_with_tolerances = False
                    record.aircraft_type = False
                elif record.TTG.name == "Special Tools":
                    record.used_for_assemblies = False
                    record.used_for_assemblies = False
                elif record.TTG.name == "Ground Support Equipment, GSE":
                    record.used_for_assemblies = False
                elif record.TTG.name == "Testbenches":
                    record.aircraft_type = False
                elif record.TTG.name == "Test measuring and digonastic Equioment, TMDEs":
                    record.aircraft_type = False
            else:
                record.what_ttg = ""

    tools_id= fields.Many2one('product.template', string = "Tools ID")
    TTG = fields.Many2one('ttg.type',string="TTG Type")
    Purpose_and_Description = fields.Text(string="Purpose and Description")
    Dimensions = fields.Text(string="Dimensions")
    measuring_value = fields.Text(string="Measuring Values Name")
    measurement_ranges_with_tolerances = fields.Many2one("tool.testbench.options",string="Measurement Ranges with Tolerances")
    used_for_assemblies = fields.Many2many("tool.testbench.options",string="Used for Assemblies")
    test_conducted = fields.Many2one("tool.testbench.options",string="Tests conducted")
    aircraft_type = fields.Many2many("fleet.vehicle.model", string="Aircraft Type")
    tools_specification = fields.One2many("tool.testbench.specification", "prod_tmpl_id", string="Specifications")
    what_ttg = fields.Char("What TTG Is Selected", default="", compute="compute_what_ttg")

class ProductTailProcurementCondition(models.Model):
    _name = 'product.tail.procurement.condition'

    name = fields.Char("Name")

class ttg_model(models.Model):
    _name = 'ttg.type'

    name = fields.Char("Name")

class ToolTestBenchYesNoOptionsSpecification(models.Model):
    _name = "tool.testbench.specification"

    name = fields.Many2one("tool.testbench.specification.names", string="Select Specification")
    description = fields.Text("Details")
    prod_tmpl_id = fields.Many2one("product.template", string="Template ID")

class ToolTestBenchYesNoOptionsSpecificationNames(models.Model):
    _name = "tool.testbench.specification.names"

    name = fields.Char("Name")

class ToolTestBenchYesNoOptions(models.Model):
    _name = "tool.testbench.options"

    name = fields.Char("Name")

class TypeConsumeableModel(models.Model):
    _name = "type.consumeable.model"

    name = fields.Char("Name")

class ProductTboSerialNumber(models.Model):
    _name = "product.tbo.serial.number"

    name = fields.Char("Name")

class TypeSPartModel(models.Model):
    _name = "type.spart.model"

    name = fields.Char("Name")

class TypeExpendableModel(models.Model):
    _name = "type.expendable.model"

    name = fields.Char("Name")

class Specification_model(models.Model):
    _name = "specification.model"

    name = fields.Char("Name")

class Specification_unit(models.Model):
    _name = "specification.unit"

    name = fields.Char("Name")

class local_manufacturer(models.Model):
    _name = "local.manufacturer"

    name = fields.Char("Name")
    p_id = fields.Many2one("product.template", "Product Template")

class local_vendors(models.Model):
    _name = "local.vendors"

    name = fields.Char("Name")

class TailProductRemovalReason(models.Model):
    _name = "tail.product.removal.reason"

    name = fields.Char("Name")

class MroaProductTradeCode(models.Model):
    _name = "mroa.product.trade.code"

    name = fields.Char("Name")

class MroaProductRelationCode(models.Model):
    _name = "mroa.product.relation.code"

    name = fields.Char("Name")

class MroaProductServiceCode(models.Model):
    _name = "mroa.product.service.code"

    name = fields.Char("Name")

class MroaProductConditionCode(models.Model):
    _name = "mroa.repair.condition.model"

    name = fields.Char("Name")

class lot(models.Model):
    _inherit = 'stock.production.lot'

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.ref = self.product_id.tail_reference

    max_calendar_life = fields.Float(string="Maximum Calander Life")
    max_calendar_life_months = fields.Float(string="Maximum Calander Life")
    max_storage_temp = fields.Float(string = "Maximum Storage Temperature")
    max_storage_humidity = fields.Float(string="Maximum Storage Humidity ")
    manufacture_date = fields.Date("Manufacture Date")
    retest_date = fields.Date("Retest Date")
    expiry_date = fields.Date("Expiry Date")

class ProductLspDesigner(models.Model):
    _name = "product.lsp.designer"

    name = fields.Char("Name")

class ProductForcastingLsp(models.Model):
    _name = "product.forcasting.lsp"

    lsp_designer = fields.Many2one("product.lsp.designer")
    project_quantity = fields.Integer("Project Quantity")
    edp_quantity = fields.Integer("EDP Aircraft Quantity Required")
    un_quantity = fields.Integer("UN Mission Quantity Required")
    forecasted_quantity = fields.One2many("product.forcasted.quantity", "f_id", string="Forecasted Quantity")
    lsp_quantity = fields.One2many("product.lsp.quantity", "lsp_id", string="LSP Quantity")
    p_temp_id = fields.Many2one("product.template", string="Product Template ID")

class ProductForcastedQuantity(models.Model):
    _name = "product.forcasted.quantity"

    f_quantity_sch = fields.Char("Forecasted Quantity Scheduled Next financial Year")
    f_quantity_unf = fields.Char("Forecasted Quantity Unforeseen Next Financial Year")
    f_quantity_tot = fields.Char("Forecasted Quantity Total Next Financial Year")
    f_id = fields.Many2one("product.forcasting.lsp")

class ProductLSPQuantity(models.Model):
    _name = "product.lsp.quantity"

    lsp_quantity_sch = fields.Char("LSP Quantity Scheduled Next financial Year")
    lsp_quantity_unf = fields.Char("LSP Quantity Unforeseen Next Financial Year")
    lsp_quantity_tot = fields.Char("LSP Quantity Total Next Financial Year")
    lsp_id = fields.Many2one("product.forcasting.lsp")

class SpecificationProdModelsNames(models.Model):
    _name = "specification.prod.models.names"

    name = fields.Char("Name")

class SpecificationProdModels(models.Model):
    _name = "specification.prod.models"

    name = fields.Many2one("specification.prod.models.names", string="Specification")
    unit = fields.Many2one("uom.uom", string="Specification Unit")
    con_prod_tmp_id = fields.Many2one("product.template", string="Product ID")
    spart_prod_tmp_id = fields.Many2one("product.template", string="Product ID")
    expand_prod_tmp_id = fields.Many2one("product.template", string="Product ID")

class MroaProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('tail_reference', False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'tail_reference', 'product_tmpl_id'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                # Filter out sellers based on the company. This is done afterwards for a better
                # code readability. At this point, only a few sellers should remain, so it should
                # not be a performance issue.
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'tail_reference': s.tail_reference or product.tail_reference,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'tail_reference': product.tail_reference,
                          }
                result.append(_name_get(mydict))
        return result
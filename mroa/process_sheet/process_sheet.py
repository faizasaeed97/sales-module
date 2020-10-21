from odoo import api, fields, models, _
from datetime import datetime
import time


class MROAProcessSheet(models.Model):
    _name = 'mroa.process.sheets'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mroa.process.sheets')
        return super(MROAProcessSheet, self).create(vals)

    name = fields.Char("Sheet ID")
    product_id = fields.Many2one("product.template", string="Internal Reference/Part No")
    p_nomenclature = fields.Char(related="product_id.name", string="Nomenclature")
    assembly_no = fields.Char(related="product_id.serial_number", string="Assembly Serial No")
    sheet_code = fields.Char("Sheet Code")
    shop_sequence = fields.Char("Shop Sequence")
    shop_name = fields.Char("Shop Name")
    qci_number = fields.Char("QCI Number")
    qci_name = fields.Char("QCI Name")
    qci_bio = fields.Char("QCI Biometric")
    qai_number = fields.Char("QAI Number")
    qai_name = fields.Char("QAI Name")
    qai_bio = fields.Char("QAI Biometric")
    # performed_by = fields.Many2one("res.users", "Performed By")
    inspector = fields.Many2one("res.users", "Supervisor Name")
    supervisor = fields.Many2one("res.users", "Supervisor Biometric")
    technician_name = fields.Many2one("hr.employee", "Technician Name")
    technician_number = fields.Char("Technician Number")
    technician_bio = fields.Char("Technician Biometric")
    mroa_workorders = fields.Many2one("mrp.production", string="Work Order")
    mroa_job_card = fields.Many2one("mrp.workorder", string="Job Card No")

    Shop_Name = fields.Char(string="Shop name")
    Sheet_Sequence_Number = fields.Char(string="Sheet Sequence Number")

    aircraft_nomenclature = fields.Many2one("mroa.aircraft.names", string="Aircraft Nomenclature")
    aircraft_model = fields.Many2one("fleet.vehicle.model", string="Aircraft Model")
    aircraft_tail_number = fields.Many2one("mroa.fleet.vehicle", string="Aircraft Tail Number/Reg No")
    aircraft_serail_number = fields.Char(related="aircraft_tail_number.vin_sn", string="Aircraft Serial No.")
    mroa_systems = fields.Many2one("mroa.system.required", string="System")
    # Quality Inspection Fields
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
    general_condition = fields.Char("General Condition")
    if_unsatisfactory = fields.Text("Unsatisfactory Reason")
    unsatisfactory = fields.Boolean(string="If Unsatisfactory")
    assembly_complete = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Assembly is Complete")
    parts_not_assembly = fields.Many2many("product.template", string="Parts Not In Assembly",
                                          domain="[('is_assembly','=',True)]")
    documents_completeness = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Completeness of documents")
    accompanying_docs = fields.Many2one("Accompanying Documentation")
    repair_accepted = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Accepted for repair")

    # visual Inspection fields
    vis_type = fields.Many2one("visual.inspection.sheet.type", string="Type")
    vis_defect_summary = fields.Text("Defect Summary")
    vis_repair_method = fields.Text("Repair Method")
    vis_type_lines = fields.One2many("visual.inspection.sheet.type.lines", "sheet_id", string="Lines")
    ass_type_lines = fields.One2many("assemblies.inspection.sheet.lines", "sheet_id", string="Lines")
    sub_ass_type_lines = fields.One2many("sub.assemblies.inspection.sheet.lines", "sheet_id", string="Lines")
    tst_cmp_assembly_lines = fields.One2many("testcmp.assemblies.sheet.lines", "sheet_id", string="Lines")
    test_bench_test_lines = fields.One2many("test.bench.test.sheet.lines", "sheet_id", string="Lines")
    repair_sheet_lines = fields.One2many("repair.sheet.lines", "sheet_id", string="Lines")
    measure_sheet_lines = fields.One2many("measurement.sheet.lines", "sheet_id", string="Lines")

    vis_inspection_reason = fields.One2many("visual.inspection.sheet.reason.lines", "sheet_id", string="Reason List")

    document_Numebr = fields.Char("Document Numebr")
    issue_Number = fields.Char("Issue Number")
    reference = fields.Char("Reference")
    issue_Date = fields.Date("Issue Date")
    effective_Date = fields.Date("Effective Date")
    revised_page = fields.Char("Revised page")
    page_no = fields.Char("Page No")
    revision_date = fields.Date("Revision Date")
    Effective_Date = fields.Date("Effective Date")
    Remarks = fields.Char("Remarks")

    installation_location = fields.Char(string="Installation Location (per manual)")
    applicablity = fields.Char(string="Applicability (Serial Numbers)")

    Prepared_by = fields.Many2one('res.users', "Prepared by")
    Reviewed_By = fields.Many2one('res.users', "Reviewed By")
    Approved_By = fields.Many2one('res.users', "Approved By")

    # Quality out inspection
    Nomenclature = fields.Char("Nomenclature")
    Assembly_Serial_No = fields.Char("Assembly Serial#")
    Work_Order_Number = fields.Many2one("mrp.production", string="Work Order number")
    pdc_date = fields.Date("pdc date")
    date_Completed = fields.Date("date Completed")
    assembly_Status = fields.Char("assembly Status")
    service_Life = fields.Char("service Life")
    calender_Life = fields.Char("calender Life")
    completeness_of_documents = fields.Char("completeness of documents")
    accompanying_documentation = fields.Char("accompanying documentation")
    ar_certificate = fields.Char("ar certificate")
    action_Step_Descrption = fields.Char("action Step Descrption")
    task_Card_Reference = fields.Char("task Card Reference")
    observation = fields.Char("observation")
    quality_certifcation = fields.One2many('mora.quality.certifcation.line', 'process_ref', "quality Certifcation")
    preserving_certification = fields.One2many('mora.preserving.certifcation.line', 'process_ref',
                                               "quality Certifcation")
    packging_certification = fields.One2many('mora.packging.certifcation.line', 'process_ref', "quality Certifcation")

    Date_time = fields.Datetime(string="Date Time Stamp", )
    Supervisor_Number = fields.Char("Supervisor Number")
    Manufacturing = fields.Char("Manufacturing")

    @api.onchange('mroa_workorders')
    def mroa_workorders_onchng(self):
        if self.mroa_workorders or self.mroa_job_card:
            rec_wo = self.mroa_workorders
            rec_jc = self.mroa_job_card

            if rec_wo.Unit:
                self.inspection_unit = rec_wo.Unit

            elif rec_jc.inspection_unit:
                self.inspection_unit = rec_jc.inspection_unit

            if rec_wo.Manufacturer:
                self.inspection_manufacturer = rec_wo.Manufacturer

            elif rec_jc.inspection_manufacturer:
                self.inspection_manufacturer = rec_jc.inspection_manufacturer

            if rec_wo.Manufacturing:
                self.Manufacturing = rec_wo.Manufacturing

            elif rec_jc.Manufacturing:
                self.Manufacturing = rec_wo.Manufacturing


            if rec_wo.inspection_manufacturing_date:
                self.inspection_manufacturing_date = rec_wo.inspection_manufacturing_date

            elif rec_jc.inspection_manufacturing_date:
                self.inspection_manufacturing_date = rec_jc.inspection_manufacturing_date

            if rec_wo.Removed_from_Helicopter:
                self.removed_heli = rec.Removed_from_Helicopter

            elif rec_jc.inspection_unit:
                self.removed_heli = rec.Removed_from_Helicopter

            if rec_wo.Unit:

            elif rec_jc.inspection_unit:

            if rec_wo.Unit:

            elif rec_jc.inspection_unit:

            if rec_wo.Unit:
            elif rec_jc.inspection_unit:
rec
            if rec_wo.Unit:
            elif rec_jc.inspection_unit:

            if rec_wo.Unit:
            elif rec_jc.inspection_unit:





            self.calendar_life_months = rec.calendar_life_months
            self.calendar_life_years = rec.calendar_life_years
            self.tsn = rec.Time_Sine_New
            self.tso = rec.Time_Since_Overhaul
            self.last_repair_at = rec.Last_Repair_At
            self.last_repair_date = rec.Last_Repair_Date
            self.Work_Order_Number = rec.id


class MROAVisualInspectionSheetTypeLines(models.Model):
    _name = "visual.inspection.sheet.type.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROAVisualInspectionSheetTypeLines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Visual Inspection' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Visual Inspection' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROAVisualInspectionSheetTypeLines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    part_no = fields.Many2one("product.template", string="Part (Assembly) Nomenclature")
    part_desc = fields.Char(string="Part Description")
    part_drawing_no = fields.Char(string="Part Drawaing No.")
    q_main_item = fields.Integer("Quantity In Main Item")
    q_reject = fields.Integer("Quantity In Rejected")
    q_for_repair = fields.Integer("Quantity In For Repair")
    q_for_walves = fields.Integer("In Walves 4 In One Engine")
    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")
    defect_summary = fields.Text(string="Defect Summary")
    repair_method = fields.Text(string="Repair Method")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')


class MROA_Quality_Certifcation(models.Model):
    _name = "mora.quality.certifcation.line"

    process_ref = fields.Many2one('mroa.process.sheets')

    assembly_Nomenclature = fields.Char("assembly Nomenclature")
    serial_Number = fields.Char("serial Number")
    biometric_QCI = fields.Char("biometric QCI")
    Biometric_QAI = fields.Char("Biometric QAI")


class MROA_preserving_certification(models.Model):
    _name = "mora.preserving.certifcation.line"

    process_ref = fields.Many2one('mroa.process.sheets')

    assembly_Nomenclature = fields.Char("assembly Nomenclature")
    serial_Number = fields.Char("serial Number")
    biometric_QCI = fields.Char("biometric QCI")
    Biometric_QAI = fields.Char("Biometric QAI")


class MROA_packging_certification(models.Model):
    _name = "mora.packging.certifcation.line"

    process_ref = fields.Many2one('mroa.process.sheets')

    assembly_Nomenclature = fields.Char("assembly Nomenclature")
    serial_Number = fields.Char("serial Number")
    biometric_QCI = fields.Char("biometric QCI")
    Biometric_QAI = fields.Char("Biometric QAI")


#
# class MROAAssembliesSheetines(models.Model):
#     _name = "assemblies.inspection.sheet.lines"
#     _inherit = ['mail.thread']
#
#     @api.model
#     def create(self, vals):
#         created = super(MROAAssembliesSheetines, self).create(vals)
#
#         if created.quality_check == "Yes":
#             get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
#             body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
#                 created.serial_no) + "' under 'Test Complete Assembly' Tab."
#             if get:
#                 created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
#                                      subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
#         return created
#
#     def write(self, vals):
#         if self.quality_check == "Yes":
#             get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
#             body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
#                 self.serial_no) + "' under 'Test Complete Assembly' Tab."
#             if get:
#                 self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
#                                   subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
#         return super(MROAAssembliesSheetines, self).write(vals)
#
#     serial_no = fields.Integer("Item Number")
#     action = fields.Char("Action")
#     action_description = fields.Text("Action Description")
#     note = fields.Text("Note")
#

class MROAVisualInspectionSheetReasonLines(models.Model):
    _name = "visual.inspection.sheet.reason.lines"
    _inherit = ['mail.thread']

    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")

    in_main = fields.Integer("Item In")
    rejected = fields.Char("Rejected")
    for_repair = fields.Char(string="For repair")


class MROAVisualInspectionSheetType(models.Model):
    _name = "visual.inspection.sheet.type"

    name = fields.Char("Name")


class MROAAssembliesSheetines(models.Model):
    _name = "assemblies.inspection.sheet.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROAAssembliesSheetines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Test Complete Assembly' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Test Complete Assembly' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROAAssembliesSheetines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    action = fields.Char("Action")
    action_description = fields.Text("Action Description")
    note = fields.Text("Note")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')
    task_card_reference = fields.Char("Task Card Reference")
    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")


class MROARepairSheetLines(models.Model):
    _name = "repair.sheet.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROARepairSheetLines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Repair' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Repair' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROARepairSheetLines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    action_description = fields.Text("Action Description")
    measurement = fields.Many2one("mroa.psheet.measurement.types", string="Measurement Type")
    measurement_value = fields.Char(string="Measurement")
    image = fields.Binary("Image")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')
    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")


class MROATestBenchTestSheetLines(models.Model):
    _name = "test.bench.test.sheet.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROATestBenchTestSheetLines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Test Bench Tests' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Test Bench Tests' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROATestBenchTestSheetLines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    p_desc = fields.Text("Parameter Descrption")
    p_m_manual = fields.Text("Parameters/Measurement Per Manual")
    actual_parameters = fields.Text("Actual Parameters/Measurement")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')
    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")


class MROAtestcmpAssembliesSheetLines(models.Model):
    _name = "testcmp.assemblies.sheet.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROAtestcmpAssembliesSheetLines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Sub Assembly Testing' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Measurements' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROAtestcmpAssembliesSheetLines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    action = fields.Char("Action")
    action_description = fields.Text("Action Description")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')
    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")


class MROASubAssembliesSheetines(models.Model):
    _name = "sub.assemblies.inspection.sheet.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROASubAssembliesSheetines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Sub Assembly Testing' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Measurements' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROASubAssembliesSheetines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    action = fields.Char("Action")
    action_description = fields.Text("Action Description")
    measure_type = fields.Many2one("mroa.psheet.measurement.types", string="Measurement Type")
    measure_unit = fields.Char(related="measure_type.unit", string="Measurement Unit")
    min_tolerence = fields.Char("Min Tolerance")
    max_tolerence = fields.Char("Max Tolerance")
    expand_code = fields.Char("Expendeable or Rework Code")
    measured_value = fields.Char("Measured Value")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')
    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")


class MROAMeasureSheetines(models.Model):
    _name = "measurement.sheet.lines"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        created = super(MROAMeasureSheetines, self).create(vals)

        if created.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + created.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                created.serial_no) + "' under 'Measurements' Tab."
            if get:
                created.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                     subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return created

    def write(self, vals):
        if self.quality_check == "Yes":
            get = self.env['res.groups'].search([('name', '=', 'Quality Control Inspector')])
            body = "Process Sheet '" + self.sheet_id.name + "' requires your attaention. Please check item number '" + str(
                self.serial_no) + "' under 'Measurements' Tab."
            if get:
                self.message_post(partner_ids=[get.users.partner_id.id], message_type="notification",
                                  subtype='mt_comment', author_id=self.env.user.partner_id.id, body=body)
        return super(MROAMeasureSheetines, self).write(vals)

    serial_no = fields.Integer("Item Number")
    drawing_no = fields.Char("Part Drawaing No.")
    sketch_img = fields.Binary("Sketch/Image/Drawing")
    measure_type = fields.Many2one("mroa.psheet.measurement.types", string="Measurement Type")
    measure_unit = fields.Char(related="measure_type.unit", string="Measurement Unit")
    min_tolerence = fields.Char("Min Tolerance")
    max_tolerence = fields.Char("Max Tolerance")
    expand_code = fields.Char("Expendeable or Rework Code")
    measured_value = fields.Char("Measured Value (Before Repair)")
    measured_value_after = fields.Char("Measured Value (After Repair)")
    quality_check = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Quality Check", default='No')
    test_name = fields.Char("Test Name")
    sub_test_name = fields.Char("Sub Test Name")
    measring_points = fields.Char("Measuring Points/Terminal/Switch Position")
    mean_value = fields.Char("Mean Value")
    mean_value = fields.Char("Mean Value")
    Date_time = fields.Datetime(string="Date Time Stamp")

    sheet_id = fields.Many2one("mroa.process.sheets", string="Process Sheet ID")


class MROAMeasureMentTypes(models.Model):
    _name = "mroa.psheet.measurement.types"

    name = fields.Char("Measurements Type")
    unit = fields.Char("Measurements Unit")

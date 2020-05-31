from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class DCQuotationSaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def getSoZones(self):
        if self.id:
            work_line = self.env['scope.work.line'].search([('saleorder', '=', self.id)], order='zones asc')
            zone = []
            last_zone = -1
            t_cost = 0
            for line in work_line:
                if line.zones:
                    if last_zone == -1 or last_zone != line.zones.id:
                        last_zone = line.zones.id
                        self._cr.execute(
                            "select sum(total_cost) as total_cst from scope_work_line where saleorder=" + str(
                                self.id) + " and zones=" + str(line.zones.id) + ";")
                        result = self._cr.dictfetchall()
                        vals = {
                            'id': line.zones.id,
                            'name': line.zones.name,
                            'total_cost': result[0]['total_cst'] or 0
                        }
                        _logger.warning("value of TOTAL_CST is '" + str(result[0]['total_cst']) + "'")
                        zone.append(vals)

            return zone

    def getZoneLines(self, zone_id):
        _logger.warning("Zone Id i get id '" + str(zone_id) + "'")
        if zone_id:
            work_line = self.env['scope.work.line'].search([('zones', '=', zone_id), ('saleorder', '=', self.id)])
            zone_lines = []
            counter = 1
            for line in work_line:
                vals = {
                    'sno': counter,
                    'p_desc': line.desc,
                    'sow': line.work_scope,
                    'total_cost': line.total_cost
                }
                zone_lines.append(vals)

            return zone_lines

    def get_default_tanda(self):
        toa = """<ol>
            <li>Delivery period – 60 to 70 working days from date of approval and receipt of advance payment.</li>
            <li>Payment as per above mentioned payment terms.</li>
            <li>Price base on the quantities of signs specified, Price is subject to revision in case of any change in specification & quantity. All prices are on rental basis only.</li>
            <li>All necessary permissions to install and fabricate shall be obtained by the client</li>
            <li>Orders once confirmed will not be cancelled; Design Creative W.L.L. will endeavor to execute the works within the delivery period but will not be responsible for delays due to unforeseen circumstances.</li>
            <li>The delivery period will commence from the date of approval of the cost proposal and payment of advance.</li>
            <li>Set up dates should be clearly mentioned to Design Creative W.L.L and site location should be freely available for fixing.</li>
            <li>Until Design Creative W.L.L receives the full payment for the works done, the works would still be a property of Design Creative W.L.L and Design Creative W.L.L. would have the right to remove/dismantle the works at their own will.</li>
            <li>This quotation is valid only if the approval is done in totality and individual cost mentioned in sub sections will not hold valid if this quotation is split and not approved as its lump sum value.</li>
            <li>This offer is valid for 15 days</li>
        </ol>
        """
        return toa

    def get_default_kindly_note(self):
        kn = """<ol>
        <li>This proposal does not include costs for AC Servicing</li>
        <li>Items not mentioned in the above scope of work shall be charged separately</li>
        <li>The fittings will be done based on our selection of materials and samples provided. Any changes will be subject to price change</li>
        </ol>"""

        return kn

    def get_default_qa(self):
        qa = """
        <p>Client acknowledges and agrees that by signing and returning this Proposal to Agency and/or by
issuing a purchase order referencing this Proposal, that Agency's Standard Terms and Conditions
for Services (either your existing signed agreement with Agency or the terms and conditions as
attached to this Proposal), shall govern the provision of Services and that Agency's Standard
Terms and Conditions for Services (the terms and conditions as attached to this Proposal) shall
supersede any different, inconsistent or pre‐printed terms appearing on the face or reverse side
of any invoice, sales order, acknowledgement, purchase order or confirmation issued by Client.</p>"""

        return qa

    quotation_subject = fields.Char("Quotation Subject")
    validity_days = fields.Integer("Valid For (Days)")
    delivery = fields.Char("Delivery")
    note = fields.Html("Terms And Conditions", default=get_default_tanda)
    kindly_note = fields.Html("Kindly Note", default=get_default_kindly_note)
    quotation_acceptane = fields.Html("Quotation Acceptance", default=get_default_qa)


class DCQuotationScopeWorkLine(models.Model):
    _inherit = "scope.work.line"

    zones = fields.Many2one("sale.order.zones", string="Zone")
    desc = fields.Text(string="Description")
    work_scope = fields.Text("Scope Of Work")


class DCQuotationZonesSelection(models.Model):
    _name = "sale.order.zones"

    name = fields.Char("Zona Name")

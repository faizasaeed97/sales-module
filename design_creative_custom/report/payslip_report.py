# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class pyslippytDetails(models.TransientModel):
    _name = 'payslip.summery.details'
    _description = "Project Report Details"

    month = fields.Selection(
        [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul')
            , ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')], 'Month',
        required=True)
    year = fields.Selection([(str(num), str(num)) for num in range(2000, (datetime.now().year) + 20)], 'Year',
                            required=True)

    # start_date = fields.Date(string='Start Date', required=True)
    # end_date = fields.Date(string='End Date', required=True)
    # stage_id = fields.Many2one('project.task.type', string="Stage", required=True)
    def get_tot_val(self, emps):
        dix = {}
        wage = 0
        tallow = 0
        hallow = 0
        gosi = 0
        net = 0
        for rec in emps:
            wage += rec.contract_id.wage
            tallow += rec.contract_id.travel_allowance
            hallow += rec.contract_id.housing_allowance
            gosi += rec.contract_id.gosi_salery
            net += rec.contract_id.housing_allowance + rec.contract_id.wage + rec.contract_id.travel_allowance
        dix['wage']=wage
        dix['tallow']=tallow
        dix['hallow']=hallow
        dix['gosi']=gosi
        dix['nets']=net
        return dix


    def print_report(self):
        plist = []
        month = self.month
        year = self.year
        grand = 0.0

        dept = self.env['hr.department'].search(
            [])

        for rec in dept:
            dix = {}
            dix['data'] = 'd'
            dix['div'] = rec.name
            plist.append(dix)

            emps = self.env['hr.employee'].search(
                [('contract_id.grade.department', '=', rec.id)])
            # gettot = self.get_tot_val(emps)
            # dix['wage'] = gettot.get('wage')
            # dix['tallow'] = gettot.get('tallow')
            # dix['hallow'] = gettot.get('hallow')
            # dix['gosi'] = gettot.get('gosi')
            # dix['nets'] = gettot.get('nets')
            # plist.append(dix)
            for dec in emps:
                slip = self.env['hr.payslip'].search(
                    [('contract_id', '=', dec.contract_id.id)])
                dix = {}
                if slip:
                    for slp in slip:
                        if slp.date_from.month == int(month) and slp.date_from.year == int(year):
                            deduc = 0.0
                            ot_tot = 0.0

                            dix['data'] = 'nd'
                            dix['div'] = rec.name
                            dix['date'] = dec.date_of_join
                            dix['emp'] = dec.name
                            dix['id'] = dec.identification_id

                            dix['worked'] = slp.consider_days
                            dix['absent'] = slp.absents
                            dix['desig'] = dec.contract_id.grade.designation.name

                            for nep in slp.line_ids:
                                if nep.category_id.name == "Deduction":
                                    deduc += nep.total
                                if nep.name in ["OT(1.5) Allowance", "OT (125) Allowance"]:
                                    ot_tot += nep.total
                                if nep.name == 'Net Salary':
                                    grand += nep.total

                                dix[nep.name] = nep.total
                            dix['deduc'] = deduc
                            dix['ot_tot'] = ot_tot
                        else:
                            dix['data'] = 'nd'
                            dix['div'] = rec.name
                            dix['date'] = dec.date_of_join
                            dix['emp'] = dec.name
                            dix['id'] = dec.identification_id


                else:
                    dix['data'] = 'nd'
                    dix['div'] = rec.name
                    dix['date'] = dec.date_of_join
                    dix['emp'] = dec.name
                    dix['id'] = dec.identification_id

                plist.append(dix)
        plist.append(
            {'data': 'n', 'grand': grand})

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'month': self.month,
                'year': self.year,
                'dta': plist
            },
        }
        return self.env.ref('design_creative_custom.pyslipxc_payslip_report_xlsx_id').report_action(self, data=data)



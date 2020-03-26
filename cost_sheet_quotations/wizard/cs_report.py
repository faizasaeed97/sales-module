# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Akshay Babu(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, api



class ProjectReportPar(models.AbstractModel):
    _name = 'report.cost_sheet_quotations.cs_order_print_template'

    def _get_report_values(self, docids, data=None):
        csid = data['cs_id']
        if csid:
            cost_sheet=self.env['cost.sheet.crm'].browse(csid)
            dicts = {}
            list=[]
            fp = -1
            for i in cost_sheet.material_ids:

                if i.product_final:
                    if dicts:
                        list.append(dicts)
                        dicts = {}
                    fp=i.product_final

                    # --subtotal--
                    fptot=0.0
                    fpmat=0.0
                    for rec in cost_sheet.scope_work:
                        if rec.product_id.id==fp.id:
                            fptot=rec.total_cost
                            fpmat=rec.mat_pur_tot

                    # --Rentals internal--
                    rent_int = 0.0
                    found=False
                    for rec in cost_sheet.internal_rental_ids:
                        if rec.product_final.id == fp.id:
                            found=True
                        if  rec.product_final and  fp.id!=rec.product_final.id:
                            found=False
                        if found:
                            rent_int += rec.subtotal


                    # --Rentals external--
                    rent_ext = 0.0
                    found = False
                    for rec in cost_sheet.outsource_rental_ids:
                        if rec.product_final.id == fp.id:
                            found = True
                        if rec.product_final and fp.id != rec.product_final.id:
                            found = False
                        if found:
                            rent_ext += rec.subtotal

                    # --Labor--
                    labor = 0.0
                    found = False
                    for rec in cost_sheet.labor_ids:
                        if rec.product_final.id == fp.id:
                            found = True
                        if rec.product_final and fp.id != rec.product_final.id:
                            found = False
                        if found:
                            labor += rec.subtotal

                    list.append({'name':fp.name,'labor':labor,'rent_int':rent_int,'rent_ext':rent_ext,'final':True,'subtotal':fptot,'material':fpmat,'display':False})

                    dicts={'subtotal':fptot,'material':fpmat,'final':False,'display':True}

                list.append({'name':i.product_id.name,'qty':i.qty,'unit':i.uom,'rate':i.rate,'subtotal':i.subtotal,'mat_pur':i.mat_purchase,'final':False,'display':False})
                if dicts and i.is_last:
                    list.append(dicts)
                    # val={}





            if list:
                return {
                    'vals': list,
                    'costsheet':cost_sheet
                }





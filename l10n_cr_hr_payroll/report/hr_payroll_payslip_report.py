# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp import models
from openerp.tools.translate import _

class hrPayrollreport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hrPayrollreport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_worked_lines': self.get_worked_lines,
            'get_payslip_lines':self.get_payslip_lines,
            'not_HE':self.not_HE,
            'not_HN':self.not_HN,
        })
       
    def get_worked_lines(self,payslip_id):
        worked_line = self.pool.get('hr.payslip.worked_days')
        worked_lines_ids = worked_line.search(self.cr,self.uid,[('payslip_id','=',payslip_id)])
        worked_lines_object = worked_line.browse(self.cr,self.uid,worked_lines_ids)
            
        return worked_lines_object
    
    def not_HE(self,worked_lines_list):
        flag = False
        
        for line in worked_lines_list:
            if line.code == 'HE' and line.number_of_hours > 0:
                flag = True
        return flag
    
    def not_HN(self,worked_lines_list):
        flag = False
        
        for line in worked_lines_list:
            if line.code == 'HN' and line.number_of_hours > 0:
                flag = True
        return flag
    
    def get_payslip_lines (self,payslip_id):
        payslip_line = self.pool.get('hr.payslip.line')
        payslip_lines_ids = payslip_line.search(self.cr,self.uid,[('slip_id','=',payslip_id),('salary_rule_id.appears_on_report','=',True)])
        payslip_lines_object = payslip_line.browse(self.cr,self.uid,payslip_lines_ids)
        payslip_lines_list = []
        base = 0
        
        for line in payslip_lines_object:
            if line.code == 'BASE':
                base = line.total
                payslip_lines_list.append(line)
            
            if line.code != 'BASE' and line.code != 'BRUTO':
                payslip_lines_list.append(line)
            
            if line.code == 'BRUTO' and line.total != base:
                payslip_lines_list.append(line)
        
        return payslip_lines_list
    
    
class hrPayroll_report(models.AbstractModel):
   _name = 'report.l10n_cr_hr_payroll.report_payslip'
   _inherit = 'report.abstract_report'
   _template = 'l10n_cr_hr_payroll.report_payslip'
   _wrapped_report_class = hrPayrollreport


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

class ReportEmployeeByPeriods(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(ReportEmployeeByPeriods, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_period_by_id': self.get_period_by_id,
            'get_payslips_by_employee': self.get_payslips_by_employee,
            'get_hn': self.get_hn,
            'get_he': self.get_he,
            'get_basic': self.get_basic,
            'get_ext': self.get_ext,
            'get_gross': self.get_gross,
            'get_ccss': self.get_ccss,
            'get_bon': self.get_bon,
            'get_rent': self.get_rent,
            'get_net': self.get_net,
            'get_RETM':self.get_RETM,
            'get_RETS':self.get_RETS,
            'get_retroactive':self.get_retroactive,
        })
    
    def get_period_by_id(self, period_id):
        account_period_obj = self.pool.get('account.period')
        period = account_period_obj.browse(self.cr, self.uid, [period_id])[0]
        return period

    def get_payslips_by_employee(self,start_period, stop_period):
        hr_payslip_object = self.pool.get('hr.payslip')
        payslips_ids = []
        payslips = []
        payslips_ids=hr_payslip_object.search(self.cr,self.uid,[('date_from', '>=' ,start_period),('date_to', '<=' , stop_period),('employee_id.user_id', '<=' , self.uid)])
        payslips = hr_payslip_object.browse(self.cr,self.uid,payslips_ids)
        return payslips
        
    def get_hn(self, payslip):
        code = 'HN'
        res = 0.00
        for line in payslip.worked_days_line_ids:
            if line.code == code:
                res += line.number_of_hours
        return res
        
    def get_he(self,payslip):
        code = 'HE'
        res = 0.00
        for line in payslip.worked_days_line_ids:
            if line.code == code:
                res += line.number_of_hours        
        return res
    
    def get_basic(self,payslip):
        code = 'BASE'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
        
    def get_ext(self, payslip):
        code = 'EXT'
        code2 = 'EXT-FE'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
            elif line.code == code2:
                res += line.total
        res = res + self.get_retroactive(payslip)
        return res
        
    def get_gross(self, payslip):
        code = 'BRUTO'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
    
    def get_ccss(self,payslip):
        code = 'CCSS-EMP'
        code2 = 'CCSS-EMP-PEN'
        code3 = 'Banco Popular-EMP'
        code4 = 'CCSS-IVM'
        code5 = 'CCSS-SEM'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
            elif line.code == code2:
                res += line.total
            elif line.code == code3:
                res += line.total
            elif line.code == code4:
                res += line.total
            elif line.code == code5:
                res += line.total
        return res
    
    def get_bon(self,payslip):
        code = 'BON'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
    
    def get_net(self, payslip):
        code = 'NETO'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res


    def get_rent(self,payslip):
        code = 'RENTA'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
    
    def get_RETM(self,payslip):
        code = 'RET-MENS'
        res = 0
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res

    def get_RETS(self,payslip):
        code = 'RET-SEM'
        res = 0
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
        
    def get_retroactive(self, payslip):
        res = 0
        res = self.get_RETS(payslip) + self.get_RETM(payslip)
        return res
    
class report_payroll_employee(models.AbstractModel):
   _name = 'report.l10n_cr_hr_payroll.report_employee_by_periods'
   _inherit = 'report.abstract_report'
   _template = 'l10n_cr_hr_payroll.report_employee_by_periods'
   _wrapped_report_class = ReportEmployeeByPeriods

#report_sxw.report_sxw(
 #   'report.hr_payroll_employee_by_periods_report',
#    'hr.payslip',
#    'addons/l10n_cr_hr_payroll/report/hr_payroll_employee_by_periods_report.mako',
#    parser=ReportEmployeeByPeriods)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

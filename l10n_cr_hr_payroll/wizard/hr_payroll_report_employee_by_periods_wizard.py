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
from openerp import models, fields, api, _

        
class ReportEmployeeByPeriodsWizard(models.TransientModel):

    _name = "report.employee.by.periods"
    _description = "Report Employee by Periods"
    
    
    company_id= fields.Many2one('res.company', 'Company',)
    period_from= fields.Many2one('account.period', 'Start Period',)
    period_to= fields.Many2one('account.period', 'End Period',)
    
    
    _defaults = {
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                     context=context).company_id.id,
    }

    @api.multi
    def print_report(self):
        p_from= self.env['account.period'].search([('id','=',self.period_from.id)])[0].date_start
        p_to= self.env['account.period'].search([('id','=',self.period_to.id)])[0].date_stop
        data = {
            'form': {
                'period_from':p_from,
                'period_to': p_to,
            }
        }
        res = self.env['report'].get_action(self.company_id,
            'l10n_cr_hr_payroll.report_employee_by_periods', data=data)
        return res

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

import openerp.tools
from openerp.osv import fields, osv
from datetime import datetime, date, timedelta
from openerp.tools.translate import _



class hrContract(osv.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """

    _inherit = 'hr.contract'
    _description = 'Employee Contract'
    _columns = {
        'schedule_pay': fields.selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', select=True),
    }

    _defaults = {
        'schedule_pay': 'monthly',
    }

class hrPaysliprun(osv.Model):
    _inherit = 'hr.payslip.run'
    _columns = {
        'schedule_pay': fields.selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', select=True, readonly=True, states={'draft': [('readonly', False)]}),      
    }
    


class hrPayslipinherit(osv.Model):
    
    _inherit = 'hr.payslip'
    
    #Get total payment per month
    def get_qty_previous_payment(self, cr, uid, employee, actual_payslip, context=None):
        payslip_ids = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        if date_to.month < 10:
            first = str(date_to.year) + "-" + "0"+str(date_to.month) + "-" + "01"
        else:
             first = str(date_to.year) + "-" +str(date_to.month) + "-" + "01"
        first_date = datetime.strptime(first, '%Y-%m-%d')
        payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('employee_id','=', employee.id), ('date_to', '>=', first_date), ('date_to','<', actual_payslip.date_from)], context=context)
        return len(payslip_ids)
        
    #Get the previous payslip for an employee. Return all payslip that are in
    #the same month than current payslip
    def get_previous_payslips(self, cr, uid, employee, actual_payslip, context=None):
        payslip_list = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        month_date_to = date_to.month
        year_date_to = date_to.year
        payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('employee_id','=', employee.id), ('date_to','<', actual_payslip.date_to)], context=context)
        
        for empl_payslip in self.pool.get('hr.payslip').browse(cr, uid, payslip_ids, context=context):
            temp_date = datetime.strptime(empl_payslip.date_to, '%Y-%m-%d')
            if (temp_date.month == month_date_to) and (temp_date.year == year_date_to):
                payslip_list.append(empl_payslip)
        
        return payslip_list
    
    #get SBA for employee (Gross salary for an employee)
    def get_SBA(self, cr, uid, employee, actual_payslip, context=None):
        SBA = 0.0
        payslip_list = self.get_previous_payslips(cr, uid, employee, actual_payslip, context=context) #list of previous payslips
        
        for payslip in payslip_list:
            for line in payslip.line_ids:
                 if line.code == 'BRUTO':
                     SBA += line.total        
        return SBA
    
    #get previous rent
    def get_previous_rent(self, cr, uid, employee, actual_payslip, context=None):
        rent = 0.0
        payslip_list = self.get_previous_payslips(cr, uid, employee, actual_payslip, context=context) #list of previous payslips
        
        for payslip in payslip_list:
            for line in payslip.line_ids:
                 if line.code == 'RENTA':
                     rent += line.total        
        return rent
    
    #Get quantity of days between two dates
    def days_between_days(self, cr, uid, date_from, date_to, context=None):
        return abs((date_to - date_from).days)
    
    #Get number of payments per month
    def qty_future_payments(self, cr, uid, payslip, context=None):
        payments = 0
        
        date_from = datetime.strptime(payslip.date_from, '%Y-%m-%d')
        date_to = datetime.strptime(payslip.date_to, '%Y-%m-%d')
        
        dbtw = (self.days_between_days(cr, uid, date_from, date_to, context=context)) + 1 #take in account previous date for start date
        next_date = date_to + timedelta(days=dbtw)
        
        month_date_to = date_to.month
        month_date_next = next_date.month
        
        while(month_date_to == month_date_next):            
            next_date = next_date + timedelta(days=dbtw)
            month_date_next = next_date.month
            payments += 1
        
        return payments

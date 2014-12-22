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

from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import fields,osv, orm

    
class hrRulesalary(osv.osv):
    _inherit = 'hr.salary.rule'

    _defaults = {
        'amount_python_compute': '''
# Available variables:
#----------------------
# payslip: object containing the payslips
# employee: hr.employee object
# contract: hr.contract object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
# worked_days: object containing the computed worked days.
# inputs: object containing the computed inputs.
# company: object of res_company. It is a browse record
# hr_salary_rule: object for call hr_salary_rule functions
# cr: cursor 
# uid: uid

# Note: returned value have to be set in the variable 'result'

result = contract.wage * 0.10''',
        'condition_python':
'''
# Available variables:
#----------------------
# payslip: object containing the payslips
# employee: hr.employee object
# contract: hr.contract object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
# worked_days: object containing the computed worked days
# inputs: object containing the computed inputs
# company: object of res_company. It is a browse record
# hr_salary_rule: object for call hr_salary_rule functions
# cr: cursor 
# uid: uid

# Note: returned value have to be set in the variable 'result'

result = rules.NET > categories.NET * 0.10''',
    }
    
    """
        In this method we add a new BrowsableObject from hr.config settings.
        This is for use rent configuration for each company and compute the rent 
        amount in a standard way.  
    """
    def satisfy_condition(self, cr, uid, rule_id, localdict, context=None):
       
        #Get user's company and hr.config.settings associated to the company
        company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        
        #Update localdict with new variable
        localdict.update({'company':company_obj})
        
        hr_salary_rule_obj = self.pool.get('hr.salary.rule') #object from hr salary rule to use in python code
        localdict.update({'hr_salary_rule':hr_salary_rule_obj})
        
        #add cr, uid at dictionary as a variables in python code
        localdict.update({'cr':cr})
        localdict.update({'uid':uid})
        
        result = super(hrRulesalary, self).satisfy_condition(cr, uid, rule_id, localdict, context=context)
        return result
    
    """
        This function is designed to be called from python code in the salary rule.
        It receive as parameters the variables that can be used by default in 
        python code on salary rule.
       
       This function compute rent for a employee
    """
    def compute_rent_employee(self, company, employee, SBT):
        subtotal = 0.0
        exceed_2 = 0.0
        exceed_1 = 0.0
        total = 0.0
        
        limit1 = company.first_limit #From hr.conf.settings, it's in company
        limit2 = company.second_limit

        spouse_amount = company.amount_per_spouse
        child_amount = company.amount_per_child

        children_numbers = employee.report_number_child
                
        #exceed second limit
        if SBT >= limit2:
            exceed_2 = SBT - limit2
            subtotal += exceed_2 * 0.15 #15% of limit2
            limit_temp = (limit2 - limit1) * 0.10 #10% of difference between limits
            subtotal += limit_temp
   
        #exceed first limit
        elif SBT >= limit1:
            exceed_1 = SBT - limit1
            subtotal += exceed_1 * 0.10 #10% of limit1
        
        if subtotal and employee.report_spouse:
            total = subtotal - spouse_amount - (child_amount * children_numbers)
        elif subtotal:
            total = subtotal - (child_amount * children_numbers)
        
        return total
    
    """
        This function is designed to be called from python code in the salary rule.
        It receive as parameters the variables that can be used by default in 
        python code on salary rule.
        
        It receive company, a parameter and it is a res.company object, but also,
        it can be declare inside in function
    """
    def compute_total_rent(self, cr, uid, company, inputs, employee, categories, payslip):
        """
            This function computes, based on previous gross salary and future 
            base salary, the rent amount for current payslip. This is a "dynamic"
            way to compute amount rent for each payslip
        """
        
        """Principal variables"""
        SBA = 0.0 #Previous Gross Salary
        SBP = 0.0 #Currently Gross Salary
        SBF = 0.0 #Future Base Salary
        SBT = 0.0 #Gross Salary Total (this is SBA + SBP + SBF)
        
        """Objects"""
        payslip_obj = self.pool.get('hr.payslip')
        
        """Other variables"""
        rent_empl_total = 0.0
        total_curr_rent = 0.0
        total_paid_rent= 0.0
        total_payments = 0
                
        """"Get total payments"""
        previous_payments = payslip_obj.get_qty_previous_payment(cr, uid, employee, payslip)
        future_payments = payslip_obj.qty_future_payments(cr, uid, payslip)
        actual_payment = 1
        total_payments = previous_payments + actual_payment + future_payments
        
        """Update payments amount"""
        SBA = payslip_obj.get_SBA(cr, uid, employee, payslip)
        SBP = categories.BRUTO
        SBF = categories.BASE * future_payments
        SBT = SBA + SBP + SBF
            
        """Compute rent"""
        rent_empl_total = self.compute_rent_employee(company, employee, SBT) #Rent for a complete month
        total_paid_rent = payslip_obj.get_previous_rent(cr,uid,employee,payslip) #Rent already paid
        total_curr_rent = (rent_empl_total - total_paid_rent) / (future_payments + actual_payment) 
            
        return total_curr_rent
    
    """
        Function that evaluated if compute rent applies to salary rule 
    """
    def python_expresion_rent(self, cr, uid, company, inputs, employee, categories, payslip):        
        total = self.compute_total_rent(cr, uid, company, inputs, employee, categories, payslip)
        if total != 0.0:
            return True
        else:
            return False

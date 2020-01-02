# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.translate import _
from odoo import models


class hrRulesalary(models.Model):

    _inherit = 'hr.salary.rule'

    _defaults = {
        'amount_python_compute': '''
# Available variables:
#----------------------
# payslip: object containing the payslips
# employee: hr.employee object
# contract: hr.contract object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories
(sum of amount of all rules belonging to that category).
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
# categories: object containing the computed salary rule categories
(sum of amount of all rules belonging to that category).
# worked_days: object containing the computed worked days
# inputs: object containing the computed inputs
# company: object of res_company. It is a browse record
# hr_salary_rule: object for call hr_salary_rule functions
# cr: cursor
# uid: uid

# Note: returned value have to be set in the variable 'result'

result = rules.NET > categories.NET * 0.10''',
    }

    def satisfy_condition(self, rule_id, localdict):
        """In this method we add a new BrowsableObject from hr.config settings.
        This is for use rent configuration for each company and compute the
        rent amount in a standard way."""

#        Get user's company and hr.config.settings associated to the company
        company_obj = self.env.user.company_id

#       Update localdict with new variable
        localdict.update({'company': company_obj})
#       object from hr salary rule to use in python code
        hr_salary_rule_obj = self.env['hr.salary.rule']
        localdict.update({'hr_salary_rule': hr_salary_rule_obj})

#       add cr, uid at dictionary as a variables in python code
        localdict.update({'cr': self._cr})
        localdict.update({'uid': self._uid})

        result = super(hrRulesalary, self).satisfy_condition(rule_id, localdict)
        return result

    def compute_rent_employee(self, company, employee, SBT):
        """This function is designed to be called from python code in the salary rule.
        It receive as parameters the variables that can be used by default in
        python code on salary rule.

        This function compute rent for a employee"""
        total = 0.0

#       From hr.conf.settings, it's in company
        limit1 = company.first_limit
        limit2 = company.second_limit
        limit3 = company.third_limit
        limit4 = company.fourth_limit

        percent1 = 0.10
        percent2 = 0.15
        percent3 = 0.20
        percent4 = 0.25

        wife_amount = company.amount_per_wife
        child_amount = company.amount_per_child
        children_numbers = employee.report_number_child

        total += max(0.0, SBT - limit4) * percent4
        total += max(0.0, min(SBT, limit4) - limit3) * percent3
        total += max(0.0, min(SBT, limit3) - limit2) * percent2
        total += max(0.0, min(SBT, limit2) - limit1) * percent1

        if total:
            if employee.report_wife:
                total = max(0.0, total - wife_amount)
            total = max(0.0, total - (child_amount * children_numbers))
        return total

# =============================================================================
#     This function is designed to be called from python code in the salary
# rule.
#     It receive as parameters the variables that can be used by default in
#     python code on salary rule.
#     It receive company, a parameter and it is a res.company object, but also,
#     it can be declare inside in function
# =============================================================================
    def compute_total_rent(self, company, inputs, employee,
                           categories, payslip):
        """
            This function computes, based on previous gross salary and future
            base salary, the rent amount for current payslip. This is a
            "dynamic" way to compute amount rent for each payslip
        """
        """Objects"""
        payslip_obj = self.env['hr.payslip']
        """
            If the payslip is a refund, we need to use the same amount
            calculated above
        """
        if payslip.credit_note:
            original_name = payslip.name.replace(_('Refund: '), '')
            original_payslip_id = payslip_obj.search([
                ('name', '=', original_name),
                ('employee_id', '=', employee.id),
                ('date_to', '=', payslip.date_to),
                ('date_from', '=', payslip.date_from)])[0]
            original_payslip = payslip_obj.browse(original_payslip_id)
            for line in original_payslip.line_ids:
                if line.code == 'RENTA':
                    return line.total
            return 0.0

        """"Get total payments"""
        future_payments = payslip_obj.qty_future_payments(payslip)
        actual_payment = 1

        """Update payments amount"""
        SBA = payslip_obj.get_SBA(employee, payslip)
        SBP = categories.BRUTO
        SBF = categories.BASE * future_payments
        SBT = SBA + SBP + SBF

        """Compute rent"""
#       Rent for a complete month
        rent_empl_total = self.compute_rent_employee(company, employee, SBT)
#       Rent already paid
        total_paid_rent = payslip_obj.get_previous_rent(employee,
                                                        payslip)
        total_curr_rent = (rent_empl_total - total_paid_rent) /\
            (future_payments + actual_payment)
        return total_curr_rent

    def python_expresion_rent(self, company, inputs, employee,
                              categories, payslip):
        """Function that evaluated if compute rent applies to salary rule"""
        total = self.compute_total_rent(company, inputs, employee,
                                        categories, payslip)
        if total != 0.0:
            return True
        else:
            return False

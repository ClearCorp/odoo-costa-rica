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

from odoo import tools,models, fields, api,_
from datetime import datetime, date, timedelta
from openerp.tools.translate import _


class hrContract(models.Model):
    """Employee contract based on the visa, work permits
    allows to configure different Salary structure"""
    _inherit = 'hr.contract'
    schedule_pay=fields.Selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', index=True,default='monthly')

class hrPaysliprun(models.Model):
    _inherit = 'hr.payslip.run'

    schedule_pay= fields.Selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', index=True, readonly=True,
               states={'draft': [('readonly', False)]})

class hrPayslipinherit(models.Model):
    _name = 'hr.payslip'
    _inherit = ['mail.thread', 'hr.payslip']

    # Get total payment per month
    def get_qty_previous_payment(self,employee,actual_payslip):
        payslip_ids = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        if date_to.month < 10:
            first = str(date_to.year) + "-" + "0"+str(date_to.month) + "-" + "01"
        else:
            first = str(date_to.year) + "-" +str(date_to.month) + "-" + "01"
        first_date = datetime.strptime(first, '%Y-%m-%d')
        payslip_ids = self.env['hr.payslip'].search([('employee_id','=', employee.id), ('date_to', '>=', first_date), ('date_to','<', actual_payslip.date_from)])
        return len(payslip_ids)

    # Get the previous payslip for an employee. Return all payslip that are in
    # the same month than current payslip
    def get_previous_payslips(self,employee,actual_payslip):
        payslip_list = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        month_date_to = date_to.month
        year_date_to = date_to.year
        payslips= self.env['hr.payslip'].search([('employee_id','=', employee.id), ('date_to','<=', actual_payslip.date_to)])
        if actual_payslip.id in payslips:
            position = payslips.index(actual_payslip.id) 
            del payslips[position] 
        
        for empl_payslip in payslips:
            temp_date = datetime.strptime(empl_payslip.date_to, '%Y-%m-%d')
            if (temp_date.month == month_date_to) and (temp_date.year == year_date_to):
                payslip_list.append(empl_payslip)
        return payslip_list

    # get SBA for employee (Gross salary for an employee)
    def get_SBA(self,employee, actual_payslip):
        SBA = 0.0
        payslip_list = self.get_previous_payslips(employee, actual_payslip) #list of previous payslips
        for payslip in payslip_list:
            for line in payslip.line_ids:
                if line.code == 'BRUTO':
                    if payslip.credit_note:
                        SBA -= line.total
                    else:
                        SBA += line.total
        return SBA

    # get previous rent
    def get_previous_rent(self,employee, actual_payslip):
        rent = 0.0
        payslip_list = self.get_previous_payslips(employee, actual_payslip) #list of previous payslips
        for payslip in payslip_list:
            for line in payslip.line_ids:
                if line.code == 'RENTA':
                    if payslip.credit_note:
                        rent -= line.total
                    else:
                        rent += line.total
        return rent

    # Get quantity of days between two dates
    def days_between_days(self,date_from, date_to):
        return abs((date_to - date_from).days)

    # Get number of payments per month
    def qty_future_payments(self,payslip):
        payments = 0

        date_from = datetime.strptime(payslip.date_from, '%Y-%m-%d')
        date_to = datetime.strptime(payslip.date_to, '%Y-%m-%d')

        dbtw = (self.days_between_days(date_from, date_to)) + 1#take in account previous date for start date

        next_date = date_to + timedelta(days=dbtw)
        month_date_to = date_to.month

        if month_date_to == 2:
            next_date = next_date - timedelta(days=2)

        month_date_next = next_date.month

        while(month_date_to == month_date_next):
            next_date = next_date + timedelta(days=dbtw)
            month_date_next = next_date.month
            payments += 1
        return payments

    def action_payslip_send(self):
        '''
        This function opens a window to compose an email, with the payslip template message loaded by default
        '''
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('l10n_cr_hr_payroll', 'email_template_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

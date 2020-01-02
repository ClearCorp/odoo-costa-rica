# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from datetime import datetime, timedelta


class hrContract(models.Model):
    """Employee contract based on the visa, work permits
    allows to configure different Salary structure"""

    _inherit = 'hr.contract'

    schedule_pay = fields.Selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', index=True, default='monthly')


class hrPaysliprun(models.Model):

    _inherit = 'hr.payslip.run'

    schedule_pay = fields.Selection([
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

    state = fields.Selection([
            ('draft', 'Draft'),
            ('verify', 'Waiting'),
            ('done', 'Done'),
            ('cancel', 'Rejected'),
        ], 'Status', index=True, readonly=True,
            copy=False, track_visibility='onchange',
            help='* When the payslip is created the status is \'Draft\'.\
            \n* If the payslip is under verification, the status is \'Waiting\'. \
            \n* If the payslip is confirmed then status is set to \'Done\'.\
            \n* When user cancel payslip the status is \'Rejected\'.')

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return 'l10n_cr_hr_payroll.mt_payslip_draft'
        elif 'state' in init_values and self.state == 'verify':
            return 'l10n_cr_hr_payroll.mt_payslip_verify'
        elif 'state' in init_values and self.state == 'done':
            return 'l10n_cr_hr_payroll.mt_payslip_done'
        elif 'state' in init_values and self.state == 'cancel':
            return 'l10n_cr_hr_payroll.mt_payslip_cancel'
        return super(hrPayslipinherit, self)._track_subtype(init_values)


    def create(self, values):
        """ Override to avoid automatic logging of creation """
        payslip_id = super(hrPayslipinherit, self).create(values)
        employee_id = values.get('employee_id', False)
        employee = self.env['hr.employee'].browse(employee_id)
        if employee and employee.address_home_id:
            self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True).message_subscribe([payslip_id], [employee.address_home_id.id])
        return payslip_id  

    # Get total payment per month
    def get_qty_previous_payment(self, employee, actual_payslip):
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        if date_to.month < 10:
            first = str(date_to.year) + "-" + "0"+str(date_to.month) + "-" +\
                "01"
        else:
            first = str(date_to.year) + "-" + str(date_to.month) + "-" + "01"
        first_date = datetime.strptime(first, '%Y-%m-%d')
        payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', employee.id),
                      ('date_to', '>=', first_date),
                      ('date_to', '<', actual_payslip.date_from)])
        return len(payslip_ids)

    # Get the previous payslip for an employee. Return all payslip that are in
    # the same month than current payslip
    def get_previous_payslips(self, employee, actual_payslip):
        payslip_list = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        month_date_to = date_to.month
        year_date_to = date_to.year
        payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', employee.id),
                      ('date_to', '<=', actual_payslip.date_to), ('id', '!=', actual_payslip.id)])
        for empl_payslip in payslip_ids:
            temp_date = datetime.strptime(empl_payslip.date_to, '%Y-%m-%d')
            if (temp_date.month == month_date_to) and\
                    (temp_date.year == year_date_to):
                payslip_list.append(empl_payslip)
        return payslip_list

    # get SBA for employee (Gross salary for an employee)
    def get_SBA(self, employee, actual_payslip):
        SBA = 0.0
        payslip_list = self.get_previous_payslips(employee, actual_payslip)
        for payslip in payslip_list:
            for line in payslip.line_ids:
                if line.code == 'BRUTO':
                    if payslip.credit_note:
                        SBA -= line.total
                    else:
                        SBA += line.total
        return SBA

    # get previous rent
    def get_previous_rent(self, employee, actual_payslip):
        rent = 0.0
        payslip_list = self.get_previous_payslips(employee, actual_payslip)
        for payslip in payslip_list:
            for line in payslip.line_ids:
                if line.code == 'RENTA':
                    if payslip.credit_note:
                        rent -= line.total
                    else:
                        rent += line.total
        return rent

    # Get quantity of days between two dates
    def days_between_days(self, date_from, date_to):
        return abs((date_to - date_from).days)

    # Get number of payments per month
    def qty_future_payments(self, payslip):
        payments = 0

        date_from = datetime.strptime(payslip.date_from, '%Y-%m-%d')
        date_to = datetime.strptime(payslip.date_to, '%Y-%m-%d')

        dbtw = (self.days_between_days(date_from, date_to)) + 1
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
        """
        This function opens a window to compose an email, with the payslip
        template message loaded by default
        """
        assert len(ids) == 1, """This option should only be used for a single
                                id at a time."""
        try:
            template_id = self.env.ref('l10n_cr_hr_payroll.email_template_payslip')
        except ValueError:
            template_id = False
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id.id,
            'target': 'new',
            'context': ctx,
        }

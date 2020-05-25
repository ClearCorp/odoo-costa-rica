# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from odoo import models, fields, api, _


class HrContract(models.Model):
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


class HrPayslipRun(models.Model):
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
        ], 'Scheduled Pay', index=True, readonly=True, states={'draft': [('readonly', False)]})


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['mail.thread', 'hr.payslip']

    # Get total payment per month
    def get_qty_previous_payment(self, employee):
        payslip_ids = []
        if self.date_to.month < 10:
            first = str(self.date_to.year) + "-" + "0" + str(self.date_to.month) + "-" + "01"
        else:
            first = str(self.date_to.year) + "-" + str(self.date_to.month) + "-" + "01"
        first_date = datetime.strptime(first, '%Y-%m-%d')
        payslip_ids = self.search([
            ('employee_id', '=', employee.id),
            ('date_to', '>=', first_date),
            ('date_to', '<', self.date_from)])
        return len(payslip_ids)

    # Get the previous payslip for an employee. Return all payslip that are in
    # the same month than current payslip
    def get_previous_payslips(self, employee):
        payslip_list = []
        month_date_to = self.date_to.month
        year_date_to = self.date_to.year
        payslips = self.search([
            ('employee_id', '=', employee.id), ('date_to', '<=', self.date_to), ('id', '!=', self.id)])

        for empl_payslip in payslips:
            if (empl_payslip.date_to.month == month_date_to) and (empl_payslip.date_to.year == year_date_to):
                payslip_list.append(empl_payslip)
        return payslip_list

    # get SBA for employee (Gross salary for an employee)
    def get_sba(self, employee):
        sba = 0.0
        payslip_list = self.get_previous_payslips(employee)  # list of previous payslips
        for payslip in payslip_list:
            for line in payslip.line_ids.filtered(lambda pl: pl.code == 'BRUTO'):
                if payslip.credit_note:
                    sba -= line.total
                else:
                    sba += line.total
        return sba

    # get previous rent
    def get_previous_rent(self, employee):
        rent = 0.0
        payslip_list = self.get_previous_payslips(employee)  # list of previous payslips
        for payslip in payslip_list:
            for line in payslip.line_ids.filtered(lambda pl: pl.code == 'RENTA'):
                if payslip.credit_note:
                    rent -= line.total
                else:
                    rent += line.total
        return rent

    # Get quantity of days between two dates
    def days_between_days(self, date_from, date_to):
        return abs((date_to - date_from).days)

    # Get number of payments per month
    def qty_future_payments(self):
        payments = 0

        dbtw = (self.days_between_days(self.date_from, self.date_to)) + 1

        next_date = self.date_to + timedelta(days=dbtw)
        month_date_to = self.date_to.month

        if month_date_to == 2:
            next_date = next_date - timedelta(days=2)

        month_date_next = next_date.month

        while month_date_to == month_date_next:
            next_date = next_date + timedelta(days=dbtw)
            month_date_next = next_date.month
            payments += 1
        return payments

    def action_payslip_send(self):
        """This function opens a window to compose an email, with the payslip template message loaded by default"""
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

    def compute_total_rent(self, inputs, employee, categories):
        """ This function computes, based on previous gross salary and future
            base salary, the rent amount for current payslip. This is a
            "dynamic" way to compute amount rent for each payslip
        """

        # If the payslip is a refund, we need to use the same amount calculated above
        if self.credit_note:
            original_name = self.name.replace(_('Refund: '), '')
            original_payslip = self.search([
                ('name', '=', original_name), ('employee_id', '=', employee.id),
                ('date_to', '=', self.date_to), ('date_from', '=', self.date_from)], limit=1)
            for line in original_payslip.line_ids:
                if line.code == 'RENTA':
                    return line.total
            return 0.0

        # Get total payments
        previous_payments = self.get_qty_previous_payment(employee)
        future_payments = self.qty_future_payments()
        actual_payment = 1
        total_payments = previous_payments + actual_payment + future_payments

        # Update payments amount
        sba = self.get_sba(employee)
        sbp = categories.BRUTO
        sbf = categories.BASE * future_payments
        sbt = sba + sbp + sbf

        # Compute rent
        rent_empl_total = self.compute_rent_employee(self.company_id, employee, sbt)  # Rent for a complete month
        total_paid_rent = self.get_previous_rent(employee)  # Rent already paid
        total_curr_rent = (rent_empl_total - total_paid_rent) / (future_payments + actual_payment)

        return total_curr_rent

    def compute_rent_employee(self, company, employee, sbt):
        """This function is designed to be called from python code in the salary rule.
        It receive as parameters the variables that can be used by default in
        python code on salary rule.

        This function compute rent for a employee"""
        subtotal = 0.0
        exceed_2 = 0.0
        exceed_1 = 0.0
        total = 0.0

        limit1 = company.first_limit  # From hr.conf.settings, it's in company
        limit2 = company.second_limit

        spouse_amount = company.amount_per_spouse
        child_amount = company.amount_per_child

        children_numbers = employee.report_number_child

        # exceed second limit
        if sbt >= limit2:
            exceed_2 = sbt - limit2
            subtotal += exceed_2 * 0.15  # 15% of limit2
            limit_temp = (limit2 - limit1) * 0.10  # 10% of difference between limits
            subtotal += limit_temp

        # exceed first limit
        elif sbt >= limit1:
            exceed_1 = sbt - limit1
            subtotal += exceed_1 * 0.10  # 10% of limit1

        if subtotal and employee.report_spouse:
            total = subtotal - spouse_amount - (child_amount * children_numbers)
        elif subtotal:
            total = subtotal - (child_amount * children_numbers)
        return total

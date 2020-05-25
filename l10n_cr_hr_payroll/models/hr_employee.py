# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.constrains('report_number_child')
    def _check_report_number_child(self):
        for employee in self:
            if employee.report_number_child < 0:
                raise UserError(_('Error! The number of child to report must be greater or equal to zero.'))
        return True

    @api.onchange('marital')
    def _onchange_marital(self):
        self.report_spouse = False

    marital = fields.Selection([
        ('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')])
    report_spouse = fields.Boolean(help="If this employee reports his spouse for rent payment")
    report_number_child = fields.Integer(
        'Number of children to report', help="Number of children to report for rent payment")
    personal_email = fields.Char()

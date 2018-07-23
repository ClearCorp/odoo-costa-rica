# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class hr_employee(models.Model):

    _inherit = 'hr.employee'

    @api.constrains('report_number_child')
    def _check_report_number_child(self):
        for employee in self:
            if employee.report_number_child < 0:
                raise Warning(
                    _("""Error! The number of child to report must be greater
                     or equal to zero."""))

    @api.onchange('marital')
    def _onchange_marital(self):
        self.report_wife = False

    marital = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'),
         ('divorced', 'Divorced')], string='Marital')
    report_wife = fields.Boolean(
        'Report Wife',
        help="If this employee reports his wife for rent payment")
    report_number_child = fields.Integer(
        'Number of children to report',
        help="Number of children to report for rent payment",
        default=0)
    personal_email = fields.Char('Personal Email')

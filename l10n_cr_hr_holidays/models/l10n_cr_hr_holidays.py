# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class hr_employee(models.Model):
    _inherit = "hr.employee"

    @api.multi
    def add_legal_leaves_per_period(self):
        for employee_obj in self:
            _sum = employee_obj.remaining_leaves +\
                employee_obj.leaves_per_period
            self.write({'remaining_leaves': _sum})

    leaves_per_period = fields.Float(
        string='Legal Leaves per Period',
        help="""Total number of legal leaves to be added
        to this employee per period."""
        )

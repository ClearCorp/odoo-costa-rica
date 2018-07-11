# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class resCompanyInherit(models.Model):

    _inherit = 'res.company'

    first_limit = fields.Float(string='First Limit',
                               digits=dp.get_precision('Payroll'))
    second_limit = fields.Float(string='Second Limit',
                                digits=dp.get_precision('Payroll'))
    amount_per_child = fields.Float(string='Amount per Child',
                                    digits=dp.get_precision('Payroll'))
    amount_per_wife = fields.Float(string='Amount per wife',
                                   digits=dp.get_precision('Payroll'))

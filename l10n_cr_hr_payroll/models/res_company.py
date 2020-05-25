# -*- coding: utf-8 -*-

from odoo import models, fields
import odoo.addons.decimal_precision as dp


class ResCompany(models.Model):
    _inherit = 'res.company'

    first_limit = fields.Float(digits=dp.get_precision('Payroll'))
    second_limit = fields.Float(digits=dp.get_precision('Payroll'))
    amount_per_child = fields.Float(digits=dp.get_precision('Payroll'))
    amount_per_spouse = fields.Float(digits=dp.get_precision('Payroll'))

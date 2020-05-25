# -*- coding: utf-8 -*-

from odoo import models, fields
import odoo.addons.decimal_precision as dp


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    first_limit = fields.Float(related="company_id.first_limit", digits=dp.get_precision('Payroll'), readonly=False)
    second_limit = fields.Float(
        related="company_id.second_limit", digits=dp.get_precision('Payroll'), readonly=False)
    amount_per_child = fields.Float(
        related="company_id.amount_per_child", digits=dp.get_precision('Payroll'), readonly=False)
    amount_per_spouse = fields.Float(
        related="company_id.amount_per_spouse", digits=dp.get_precision('Payroll'), readonly=False)

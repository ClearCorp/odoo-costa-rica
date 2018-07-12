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

from openerp.tools.translate import _
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class hrSettingsConf(models.TransientModel):
    _inherit = 'hr.payroll.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    first_limit= fields.Float(related="company_id.first_limit", string='First Limit', digits=dp.get_precision('Payroll'),default=0.0)
    second_limit=fields.Float(related="company_id.second_limit",string='Second Limit', digits=dp.get_precision('Payroll'),default=0.0) 
    amount_per_child= fields.Float(related="company_id.amount_per_child",string='Amount per Child', digits=dp.get_precision('Payroll'),default=0.0)
    amount_per_spouse= fields.Float(related="company_id.amount_per_spouse",string='Amount per spouse', digits=dp.get_precision('Payroll'),default=0.0)

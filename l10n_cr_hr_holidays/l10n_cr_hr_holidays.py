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

class hr_employee(models.Model):
    _inherit="hr.employee"
    
    def add_legal_leaves_per_period(self):
        employees = self.search([])
        for employee_obj in employees:
            sum = employee_obj.remaining_leaves + employee_obj.leaves_per_period
            employee_obj.write({'remaining_leaves': sum})
    
    leaves_per_period= fields.Float(string='Legal Leaves per Period',
                                    help='Total number of legal leaves to be added to this employee per period.')

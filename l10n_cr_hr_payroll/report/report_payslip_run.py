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

from openerp.report import report_sxw
from odoo import models, fields, api, _
import odoo


class PayslipRunReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(PayslipRunReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_payslips_by_department': self._get_payslips_by_department,
            'get_worked_days_hours': self._get_worked_days_hours,
            'get_worked_days_hours_group': self._get_worked_days_hours_group,
            'get_line_total': self._get_line_total,
            'get_line_total_group': self._get_line_total_group,
        })

    def _get_payslips_by_department(self, payslip_run):
        dep_list = []
        env = odoo.api.Environment(self.cr, self.uid, {})
        department_obj = env['hr.department']
        # Create a list of departments
        for payslip in payslip_run.slip_ids:
            department_id = payslip.employee_id.department_id.id
            if department_id not in dep_list:
                dep_list.append(department_id)
        res = {}
        for department_id in dep_list:
            dep_emp = []
            for payslip in payslip_run.slip_ids:
                if payslip.employee_id.department_id.id == department_id:
                    dep_emp.append(payslip)
            department = department_obj.browse(department_id)
            res[department_id] = (department, dep_emp)
        return res

    def _get_worked_days_hours(self, payslip, code='HN'):
        total = 0.00
        for line in payslip.worked_days_line_ids:
            if line.code == code:
                if payslip.credit_note:
                    # normal schedule in Costa Rica
                    total -= line.number_of_hours + \
                        line.number_of_days * 8.0
                else:
                    total += line.number_of_hours + \
                        line.number_of_days * 8.0
        return total

    def _get_worked_days_hours_group(self, payslip, code=['HE', 'HEF', 'FE']):
        total = 0.00
        for line in payslip.worked_days_line_ids:
            if line.code in code:
                if payslip.credit_note:
                    # normal schedule in Costa Rica
                    total -= line.number_of_hours + \
                        line.number_of_days * 8.0
                else:
                    total += line.number_of_hours + \
                        line.number_of_days * 8.0
        return total

    def _get_line_total(self, payslip, code='BASE'):
        total = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                if payslip.credit_note:
                    total -= line.total
                else:
                    total += line.total
        return total

    def _get_line_total_group(self, payslip, code=['EXT', 'EXT-FE', 'FE']):
        total = 0.00
        for line in payslip.line_ids:
            if line.code in code:
                if payslip.credit_note:
                    total -= line.total
                else:
                    total += line.total
        return total


class report_payslip_run(models.AbstractModel):
    _name = 'report.l10n_cr_hr_payroll.report_payslip_run'
    _inherit = 'report.abstract_report'
    _template = 'l10n_cr_hr_payroll.report_payslip_run'
    _wrapped_report_class = PayslipRunReport

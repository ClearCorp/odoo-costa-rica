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


class ReportPayrollXLS(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportPayrollXLS, self).__init__(
                cr, uid, name, context=context)
        self.localcontext.update({
            'get_payslips_by_struct': self._get_payslips_by_struct,
            'get_payslips_by_employee': self._get_payslips_by_employee,
            'get_worked_days_hours': self._get_worked_days_hours,
            'get_worked_days_hours_group': self._get_worked_days_hours_group,
            'get_line_total': self._get_line_total,
            'get_line_total_group': self._get_line_total_group,
        })

    def _get_payslips_by_period(self, start_period, stop_period):
        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_obj =env['hr.payslip']
        payslips = []
        payslips = payslip_obj.search([('date_from', '>=', start_period),
             ('date_to', '<=', stop_period)])
        return payslips

    def _get_payslips_by_struct(self, start_period, stop_period):
        all_payslips = self._get_payslips_by_period(start_period, stop_period)
        obj_by_struct = []
        struct_list = []
        payslip_by_struct = []

        for payslip in all_payslips:
            struct_name = payslip.struct_id.name
            if struct_name not in struct_list:
                struct_list.append(struct_name)
        for struct in struct_list:
            struct_payslip = []
            for payslip in all_payslips:
                if payslip.struct_id.name == struct:
                    struct_payslip.append(payslip)
            obj_by_struct.append(struct_payslip)
        i = 0
        for struct in struct_list:
            tup_temp = (struct, obj_by_struct[i])
            payslip_by_struct.append(tup_temp)
            i += 1
        return payslip_by_struct

    def _get_payslips_by_employee(self, all_payslips):
        employee_list = []
        env = odoo.api.Environment(self.cr, self.uid, {})
        employee_obj = env['hr.employee']
        # Create a list of employees
        for payslip in all_payslips:
            employee_id = payslip.employee_id.id
            if employee_id not in employee_list:
                employee_list.append(employee_id)
        # Assign the payslip to each employee:
        res = {}
        for employee_id in employee_list:
            employee_payslips = []
            for payslip in all_payslips:
                if payslip.employee_id.id == employee_id:
                    employee_payslips.append(payslip)
            employee = employee_obj.browse(employee_id)
            res[employee_id] = (employee, employee_payslips)
        return res

    def _get_worked_days_hours(self, payslips, code='HN'):
        total = 0.00
        for payslip in payslips:
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

    def _get_worked_days_hours_group(self, payslips, code=['HE', 'HEF', 'FE']):
        total = 0.00
        for payslip in payslips:
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

    def _get_line_total(self, payslips, code='BASE'):
        total = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == code:
                    if payslip.credit_note:
                        total -= line.total
                    else:
                        total += line.total
        return total

    def _get_line_total_group(self, payslips, code=['EXT', 'EXT-FE', 'FE']):
        total = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code in code:
                    if payslip.credit_note:
                        total -= line.total
                    else:
                        total += line.total
        return total


class report_payroll_periods(models.AbstractModel):
    _name = 'report.l10n_cr_hr_payroll.report_payroll_xls'
    _inherit = 'report.abstract_report'
    _template = 'l10n_cr_hr_payroll.report_payroll_xls'
    _wrapped_report_class = ReportPayrollXLS

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

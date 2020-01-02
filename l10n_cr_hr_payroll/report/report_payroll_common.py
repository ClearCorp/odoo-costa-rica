# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api
from odoo.report import report_sxw

class ReportPayrollParent(models.AbstractModel):
    _register = False

    def _get_payslips_by_period(self, start_period, stop_period):
        payslip_obj = self.env['hr.payslip']
        payslips = []
        payslips_ids = payslip_obj.search([('date_from', '>=', start_period),
             ('date_to', '<=', stop_period)])
        if len(payslips_ids) > 0:
            payslips = payslips_ids
        return payslips

    def _get_totales(self, allPayslip):
        totales = {}
        for payslip in allPayslip:
            payslips = payslip[1]
            moneda = payslips[0].currency_id
            if not moneda:
                moneda = payslips[0].journal_id.company_id.currency_id
            if not totales.get(moneda.name):
                totales[moneda.name] = {}

            if not len(totales[moneda.name].keys()):
                totales[moneda.name] = {
                    'title': "Total " + moneda.name,
                    'total_nrm_hrs': self._get_worked_days_hours(payslips, code='HN'),
                    'total_ext_hrs': self._get_worked_days_hours_group(payslips,
                                                                       code=['HE', 'HEF', 'FE', 'EXT-FE', 'EXT']),
                    'total_base': self._get_line_total(payslips, code='BASE'),
                    'total_extra': self._get_line_total_group(payslips, code=['EXT']),
                    'total_extra_feriados': self._get_line_total_group(payslips, code=['EXT-FE', 'FE']),
                    'total_rebajo': self._get_line_total(payslips, code='HR'),
                    'total_otros_rebajos': self._get_line_total(payslips, code='OTRASDED'),
                    'total_gross': self._get_line_total(payslips, code='BRUTO'),
                    'total_deduct': self._get_line_total_group(payslips, code=['CSO']),
                    'total_bonuses': self._get_line_total(payslips, code='BON'),
                    'total_rent': self._get_line_total(payslips, code='RENTA'),
                    'total_net': self._get_line_total(payslips, code='NETO'),
                    'total_paid': self._get_line_total(payslips, code='DEVENGADO')
                }
            else:
                totales[moneda.name]['total_nrm_hrs'] += self._get_worked_days_hours(payslips, code='HN')
                totales[moneda.name]['total_ext_hrs'] += self._get_worked_days_hours_group(payslips,
                                                                                           code=['HE', 'HEF', 'FE',
                                                                                                 'EXT-FE', 'EXT'])
                totales[moneda.name]['total_base'] += self._get_line_total(payslips, code='BASE')
                totales[moneda.name]['total_extra'] += self._get_line_total_group(payslips, code=['EXT'])
                totales[moneda.name]['total_extra_feriados'] += self._get_line_total_group(payslips,
                                                                                           code=['EXT-FE', 'FE'])

                totales[moneda.name]['total_rebajo'] += self._get_line_total(payslips, code='BRUTO')
                totales[moneda.name]['total_otros_rebajos'] += self._get_line_total(payslips, code='BRUTO')

                totales[moneda.name]['total_gross'] += self._get_line_total(payslips, code='BRUTO')
                totales[moneda.name]['total_deduct'] += self._get_line_total_group(payslips, code=['CSO'])
                totales[moneda.name]['total_bonuses'] += self._get_line_total(payslips, code='BON')
                totales[moneda.name]['total_rent'] += self._get_line_total(payslips, code='RENTA')
                totales[moneda.name]['total_net'] += self._get_line_total(payslips, code='NETO')
                totales[moneda.name]['total_paid'] += self._get_line_total(payslips, code='DEVENGADO')
        return totales.values()

    def _get_payslips_by_struct(self, start_period, stop_period):
        all_payslips = self._get_payslips_by_period(start_period, stop_period)
        struct_list = {}
        payslip_by_struct = []

        for payslip in all_payslips:
            struct_name = payslip.struct_id.name
            if struct_name not in struct_list:
                struct_list.update({struct_name: {}})
        for struct in struct_list:
            for payslip in all_payslips:
                if payslip.struct_id.name == struct:
                    moneda = payslip.currency_id
                    if not moneda:
                        moneda = payslip.journal_id.company_id.currency_id
                    if not struct_list[struct].get(moneda, False):
                        struct_list[struct][moneda] = []
                    struct_list[struct][moneda].append(payslip)
        for struct in struct_list:
            for currency in struct_list[struct]:
                tup_temp = (struct + " " + currency.name, struct_list[struct][currency])
                payslip_by_struct.append(tup_temp)
        return payslip_by_struct

    def _get_payslips_by_employee(self, all_payslips):
        employee_list = []
        employee_obj = self.env['hr.employee']
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


    def _get_payslips_by_department(self, payslip_run):
        dep_list = []
        department_obj = self.env['hr.department']
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


    @api.model
    def render_html(self, docids, data=None):
        formatLang = report_sxw.rml_parse(self._cr, self._uid, 'l10n_cr_hr_payroll.report_payroll_periods').formatLang
        docargs = {
            'docids':docids,
            'data': data,
            'formatLang': formatLang,
            'get_payslips_by_department': self._get_payslips_by_department,
            'get_payslips_by_struct': self._get_payslips_by_struct,
            'get_payslips_by_employee': self._get_payslips_by_employee,
            'get_worked_days_hours': self._get_worked_days_hours,
            'get_worked_days_hours_group': self._get_worked_days_hours_group,
            'get_line_total': self._get_line_total,
            'get_line_total_group': self._get_line_total_group,
            'get_totales': self._get_totales,
        }

        return self.env['report'].render(self._name.replace('report.', ''), docargs)

class report_payroll_periods_employee(ReportPayrollParent):
    _name = 'report.l10n_cr_hr_payroll.report_payroll_periods_employee'

class report_payroll_periods(ReportPayrollParent):
    _name = 'report.l10n_cr_hr_payroll.report_payroll_periods'

class report_payroll_periods_employee_xls(ReportPayrollParent):
    _name = 'report.l10n_cr_hr_payroll.report_payroll_xls_employee'

class report_payroll_periods_xls(ReportPayrollParent):
    _name = 'report.l10n_cr_hr_payroll.report_payroll_xls'

class report_payslip_run(ReportPayrollParent):
    _name = 'report.l10n_cr_hr_payroll.report_payslip_run'

class report_payslip_run_xls(ReportPayrollParent):
    _name = 'report.l10n_cr_hr_payroll.report_payslip_run_xls'

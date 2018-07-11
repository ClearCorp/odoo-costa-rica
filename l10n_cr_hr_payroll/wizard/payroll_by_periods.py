# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class PayrollReport(models.TransientModel):
    """Payroll Report"""

    _name = 'l10n.cr.hr.payroll.by.periods'
    _description = __doc__

    company_id = fields.Many2one('res.company', string='Company')
    format = fields.Selection(
        [('qweb-pdf', 'PDF'), ('qweb-xls', 'XLS')],
        string='Format', default='qweb-pdf')
    filter = fields.Selection(
        [('date', 'Date'), ('period', 'Period')],
        string='Filter', default='period')
    period_from = fields.Many2one('account.period', string='Start Period')
    period_to = fields.Many2one('account.period', string='End Period')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')

    _defaults = {
        'company_id': lambda self, cr, uid, context:
            self.pool.get('res.users').browse(
                cr, uid, uid,
                context=context).company_id.id,
    }

    @api.multi
    def print_report(self):
        if self.filter == 'period':
            date_from = self.env['account.period'].search(
                [('id', '=', self.period_from.id)])[0].date_start
            date_to = self.env['account.period'].search(
                [('id', '=', self.period_to.id)])[0].date_stop
        else:
            date_from = self.date_from
            date_to = self.date_to
        data = {
            'period_from': date_from,
            'period_to': date_to,
        }
        if self.format == 'qweb-pdf':
            res = self.env['report'].get_action(
                self.company_id,
                'l10n_cr_hr_payroll.report_payroll_periods',
                data=data)
        else:
            res = self.env['report'].get_action(
                self.company_id,
                'l10n_cr_hr_payroll.report_payroll_xls',
                data=data)
        return res

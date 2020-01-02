# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    d_151_type = fields.Selection([
        ('V', 'Goods and services sales'),
        ('C', 'Goods and services purchases'),
        ('A', 'Rent'),
        ('SP', 'Profesional services'),
        ('M', 'Commissions'),
        ('I', 'Interest'),
        ], string='D-151 Type', readonly=True)

    # Add into query the D-151-type field
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + \
            ", sub.d_151_type as d_151_type"
    
    # Add into query the D-151-type field
    def _sub_select(self):
        select_str = super(AccountInvoiceReport, self)._sub_select()
        new_str = select_str.replace(
            'ai.payment_term_id,',
            'ai.payment_term_id, ail.d_151_type AS d_151_type,')
        return new_str

    # Add into query the D-151-type field
    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        new_str = group_by_str.replace(
            'GROUP BY ail.product_id,',
            'GROUP BY ail.product_id, ail.d_151_type,')
        return new_str

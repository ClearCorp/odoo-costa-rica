# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice.line'

    @api.model
    def _get_type_invoice(self):
        if self._context is None:
            self._context = {}
        return self._context.get('type')

    @api.depends('invoice_id.type')
    def _get_type_invoice_line(self):
        for line in self:
            line.type_invoice = line.invoice_id.type

    # This field add category D-151 to invoice line.
    d_151_type = fields.Selection([
        ('V', 'Goods and services sales'),
        ('C', 'Goods and services purchases'),
        ('A', 'Rent'),
        ('SP', 'Profesional services'),
        ('M', 'Commissions'),
        ('I', 'Interest'),
        ], string='D-151 Type')
    type_invoice = fields.Char(
        compute='_get_type_invoice_line', string='Invoice type', size=64,
        default=_get_type_invoice)

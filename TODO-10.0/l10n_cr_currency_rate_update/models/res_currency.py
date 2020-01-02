# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


class ResCurrencyRate(models.Model):

    _inherit = 'res.currency.rate'

    name = fields.Date('Date', required=True, select=True)


class ResCurrency(models.Model):

    _inherit = 'res.currency'

    base = fields.Boolean('Base', default=False)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if 'base' in vals.keys() and vals['base']:
            if self.search_count([('base', '=', True)]) >= 1:
                raise ValidationError(
                    _('More than one currency set as base.'))
        return super(ResCurrency, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'base' in vals.keys() and vals['base']:
            if self.search_count([('base', '=', True)]) >= 1:
                raise ValidationError(
                    _('More than one currency set as base.'))
        return super(ResCurrency, self).write(vals)

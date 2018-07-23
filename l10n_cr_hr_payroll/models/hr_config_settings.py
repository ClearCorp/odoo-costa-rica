# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class HRSettingsConf(models.TransientModel):

    _inherit = 'hr.payroll.config.settings'

    rent_company_id = fields.Many2one('res.company', string='Company',
                                      required=True)
    first_limit = fields.Float(
        string='First Limit', digits=dp.get_precision('Payroll'),
        default=0.0)
    second_limit = fields.Float(
        string='Second Limit', digits=dp.get_precision('Payroll'),
        default=0.0)
    amount_per_child = fields.Float(
        string='Amount per Child', digits=dp.get_precision('Payroll'),
        default=0.0)
    amount_per_wife = fields.Float(
        string='Amount per wife', digits=dp.get_precision('Payroll'),
        default=0.0)

    """Override onchange_company_id to update rent limits """
    @api.onchange('rent_company_id')
    def onchange_rent_company_id(self):
        if self.rent_company_id:
            self.first_limit = self.rent_company_id.first_limit
            self.second_limit = self.rent_company_id.second_limit
            self.amount_per_child = self.rent_company_id.amount_per_child
            self.amount_per_wife = self.rent_company_id.amount_per_wife
        else:
            self.first_limit = 0.0
            self.second_limit = 0.0
            self.amount_per_child = 0.0
            self.amount_per_wife = 0.0

    """Get the default company for the module"""
    @api.model
    def get_default_rent_company_id(self, fields):
        return {
            'rent_company_id':
                self.env['res.company']._company_default_get().id
        }

    """Get the default first_limit"""
    @api.model
    def get_first_limit(self, fields):
        company = self.env['res.company']._company_default_get()
        return {'first_limit': company.first_limit}

    """Set the default first_limit"""
    @api.multi
    def set_first_limit(self):
        for wizard in self:
            wizard.rent_company_id.write({'first_limit': self.first_limit})

    """Get the default second_limit"""
    @api.model
    def get_second_limit(self, fields):
        company = self.env['res.company']._company_default_get()
        return {'second_limit': company.second_limit}

    """Set the default second_limit in the selected company"""
    @api.multi
    def set_second_limit(self):
        for wizard in self:
            wizard.rent_company_id.write({'second_limit': self.second_limit})

    """Get the default amount_per_child"""
    @api.model
    def get_amount_per_child(self, fields):
        company = self.env['res.company']._company_default_get()
        return {'amount_per_child': company.amount_per_child}

    """Set the default amount_per_child in the selected company"""
    @api.multi
    def set_amount_per_child(self):
        for wizard in self:
            wizard.rent_company_id.write(
                {'amount_per_child': self.amount_per_child})

    """Get the default amount_per_wife"""
    @api.model
    def get_amount_per_wife(self, fields):
        company = self.env['res.company']._company_default_get()
        return {'amount_per_wife': company.amount_per_wife}

    """Set the default amount_per_wife in the selected company"""
    @api.multi
    def set_amount_per_wife(self):
        for wizard in self:
            wizard.rent_company_id.write(
                {'amount_per_wife': self.amount_per_wife})

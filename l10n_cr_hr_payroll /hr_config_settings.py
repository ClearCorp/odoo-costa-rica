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
from openerp.osv import fields,osv, orm
import openerp.addons.decimal_precision as dp

class hrSettingsConf(osv.osv_memory):
    _inherit = 'hr.config.settings'
    
    _columns = {
        'rent_company_id': fields.many2one('res.company', string='Company', required=True),
        'first_limit': fields.float('First Limit', digits_compute=dp.get_precision('Payroll')),
        'second_limit':fields.float('Second Limit', digits_compute=dp.get_precision('Payroll')), 
        'amount_per_child': fields.float('Amount per Child', digits_compute=dp.get_precision('Payroll')),
        'amount_per_spouse': fields.float('Amount per spouse', digits_compute=dp.get_precision('Payroll')),
    }
    
    _defaults = {
        'first_limit': 0.0,
        'second_limit': 0.0,
        'amount_per_child': 0.0,
        'amount_per_spouse':0.0,
    }

    """Override onchange_company_id to update rent limits """ 
    def onchange_rent_company_id(self, cr, uid, ids, rent_company_id, context=None):
        vals = {}
        if rent_company_id:
            company = self.pool.get('res.company').browse(cr, uid, rent_company_id, context=context)
            vals = {
                'first_limit': company.first_limit,
                'second_limit':company.second_limit, 
                'amount_per_child': company.amount_per_child,
                'amount_per_spouse':company.amount_per_spouse, 
            }            
        else:
            vals = {
                'first_limit': 0.0,
                'second_limit': 0.0, 
                'amount_per_child':0.0,
                'amount_per_spouse':0.0,
             }
            
        return {'value': vals}
                
    def get_default_rent_company_id(self, cr, uid, fields, context=None):
        """Get the default company for the module"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'l10n.cr.hr.payroll', context=context)
        return {'rent_company_id': company_id}
    
    """Get the default first_limit"""
    def get_first_limit(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'l10n.cr.hr.payroll', context=context) #module name
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'first_limit': company.first_limit}
    
    """Set the default first_limit"""
    def set_first_limit(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        config.rent_company_id.write({'first_limit': config.first_limit})
    
    """Get the default second_limit"""
    def get_second_limit(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'l10n.cr.hr.payroll', context=context) #module name
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'second_limit': company.second_limit}
    
    """Set the default second_limit in the selected company"""
    def set_second_limit(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        config.rent_company_id.write({'second_limit': config.second_limit})
    
    """Set the default amount_per_child in the selected company"""
    def set_amount_per_child(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        config.rent_company_id.write({'amount_per_child': config.amount_per_child})
        
    """Get the default amount_per_child"""
    def get_amount_per_child(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'l10n.cr.hr.payroll', context=context) #module name
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'amount_per_child': company.amount_per_child}
    
    """Set the default amount_per_spouse in the selected company"""
    def set_amount_per_spouse(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        config.rent_company_id.write({'amount_per_spouse': config.amount_per_spouse})
    
    """Get the default amount_per_spouse"""
    def get_amount_per_spouse(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'l10n.cr.hr.payroll', context=context) #module name
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'amount_per_spouse': company.amount_per_spouse}

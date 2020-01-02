# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp.tools.translate import _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        name = self.read(cr, uid, id, ['name'], context=context)['name']
        default = default.copy()
        default.update({'name': name + _(' (Copy)')})
        return super(ResPartner, self).copy_data(cr, uid, id, default=default,
                                                 context=context)

    _sql_constraints = [
        ('name_reference_unique',
         'UNIQUE(ref,name)',
         'Already exist a reference associated with the name')
        ]

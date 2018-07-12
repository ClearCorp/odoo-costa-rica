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

{
    'name': 'l10n_cr_hr_holidays',
    'version': '1.0',
    'category': 'Human Resources',
    "sequence": 38,
    'complexity': "normal",
    'description': """
l10n_cr_hr_holidays
===================
    *Legal leaves per period
    *Scheduled legal leaves calculations per period
""",
    'author': 'ClearCorp',
    'website': 'http://www.clearcorp.co.cr',
    'depends': [
        'hr_holidays'
    ],
    'data': [
             'l10n_cr_hr_holidays_view.xml',
             'leaves_per_period_scheduled_task.xml',
             ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
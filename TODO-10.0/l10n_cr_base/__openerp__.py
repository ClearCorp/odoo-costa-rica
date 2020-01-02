# -*- coding: utf-8 -*-
# © <YEAR(S)> ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'l10n_cr_base',
    'summary': 'Constraint for name and internal reference',
    'version': '9.0.1.0',
    'category': 'Base',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner.xml',
    ],
}

# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Costa Rica Currency Rate Update',
    'summary': 'Rates from Costa Rica',
    'version': '9.0.1.0',
    'category': 'Financial Management/Configuration',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'currency_rate_update'
    ],
    'data': [
        'views/l10n_cr_currency_rate_update_view.xml',
    ],
}

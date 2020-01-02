# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'l10n_cr_hr_holidays',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': "",
    'author': 'ClearCorp',
    'website': 'http://www.clearcorp.cr',
    'depends': [
        'hr_holidays'
    ],
    'data': [
        'views/l10n_cr_hr_holidays_view.xml',
        'data/leaves_per_period_scheduled_task.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

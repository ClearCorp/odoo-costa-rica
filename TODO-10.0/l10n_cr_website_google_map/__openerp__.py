# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website Google Map Costa Rica',
    'summary': 'Google Map for Costa Rica',
    'version': '9.0.1.0',
    'category': 'Website',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'website_google_map',
    ],
    'data': [
        'views/website_view.xml',
    ],
}

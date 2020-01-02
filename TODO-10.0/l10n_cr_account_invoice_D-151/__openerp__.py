# -*- coding: utf-8 -*-
# © <YEAR(S)> ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'D-151 for Account Invoice',
    'summary': 'Add category to account.invoice.line for apply the D-151 ',
    'version': '9.0.1.0',
    'category': 'Accounting & Finance',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'account',
    ],
    'data': [
        'views/l10n_cr_account_invoice_line.xml',
        'views/l10n_cr_account_invoice_report.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

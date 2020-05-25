# -*- coding: utf-8 -*-

{
    'name': 'Payroll Localization - Costa Rica',
    'version': '12.0.1.0.0',
    'category': 'Localization',
    'author': 'Vauxoo,ClearCorp',
    'website': 'http://vauxoo.com',
    'license': 'LGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'data/l10n_cr_hr_payslip_action_data.xml',
        'data/l10n_cr_hr_payroll_salary_rule_category.xml',
        'data/l10n_cr_hr_payroll_salary_rule.xml',
        'views/res_config_settings_views.xml',
        'views/hr_payroll_view.xml',
        'security/l10n_cr_hr_payroll_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}

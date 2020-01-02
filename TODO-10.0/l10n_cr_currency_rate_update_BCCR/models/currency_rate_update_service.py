# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp import exceptions
from openerp.addons.currency_rate_update.services.currency_getter_interface \
    import CurrencyGetterType


_logger = logging.getLogger(__name__)
_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
}


class CurrencyRateUpdateService(models.Model):

    _inherit = 'currency.rate.update.service'

    code_rate = fields.Char('Code rate', size=64)  # Code update service

    @api.one
    def refresh_currency(self):
        if self.service != 'BCCR':
            return super(CurrencyRateUpdateService, self).refresh_currency()

        # Update for BCCR service
        # Log Service usage
        _logger.info(
            'Starting to refresh currencies with service %s (company: %s)',
            self.service, self.company_id.name)

        rate_obj = self.env['res.currency.rate']
        currency_obj = self.env['res.currency']

        company = self.company_id

        # Verify if currency update
        if company.auto_currency_up:
            main_currency = currency_obj.search([('base', '=', True)], limit=1)
            if not main_currency:
                raise exceptions.Warning(
                    _('There is no base currency defined.'))

            note = self.note or ''
            try:
                # Initalize the class that will handle the request
                # and return a dict of rate
                getter = CurrencyGetterType.get(self.service)
                curr_to_fetch = [x.name for x in self.currency_to_update]
                res, log_info = getter.get_updated_currency(
                    curr_to_fetch, main_currency.name,
                    self.max_delta_days, self.code_rate)

                rate_name = \
                    fields.Date.today()

                for curr in self.currency_to_update:
                    if curr.id == main_currency.id:
                        continue
                    do_create = True
                    for rate in curr.rate_ids:
                        if rate.name == rate_name:
                            rate.rate = res[curr.name]
                            do_create = False
                            break
                    if not res[curr.name]:
                        do_create = False

                    if do_create:
                        vals = {
                            'currency_id': curr.id,
                            'rate': res[curr.name],
                            'name': rate_name
                        }
                        rate_obj.create(vals)
                        _logger.info(
                            'Updated currency %s via service %s',
                            curr.name, self.service)

                # Show the most recent note at the top
                msg = '%s \n%s currency updated. %s' % (
                    log_info or '',
                    fields.Datetime.to_string(datetime.today()),
                    note
                )
                self.write({'note': msg})
            except Exception as exc:
                error_msg = '\n%s ERROR : %s %s' % (
                    fields.Datetime.to_string(datetime.today()),
                    repr(exc),
                    note
                )
                _logger.error(repr(exc))
                self.write({'note': error_msg})
            if self._context.get('cron', False):
                midnight = time(0, 0)
                next_run = (datetime.combine(
                            fields.Date.from_string(self.next_run),
                            midnight) +
                            _intervalTypes[str(self.interval_type)]
                            (self.interval_number)).date()
                self.next_run = next_run
        return True

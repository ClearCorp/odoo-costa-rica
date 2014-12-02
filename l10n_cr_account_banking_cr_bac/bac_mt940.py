# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
#    All Rights Reserved
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
# Import of BAC data in Swift MT940 format
#

from openerp.addons.account_banking_ccorp.parsers import models
from mt940_parser import BACParser
import re
from openerp.osv import osv, fields
import logging
import datetime
from openerp.tools.translate import _
import base64

bt = models.mem_bank_transaction
logger = logging.getLogger('bac_mt940')

def record2float(record, value):
    if record['creditmarker'][-1] == 'C':
        return float(record[value])
    return -float(record[value])

class transaction(models.mem_bank_transaction):

    mapping = {
        'execution_date' : 'valuedate',
        'effective_date' : 'valuedate',
        'local_currency' : 'currency',
        'transfer_type' : 'bookingcode',
        'reference' : 'custrefno',
        'message' : 'furtherinfo',
        'name' : 'infoline1'
    }

    type_map = {
        'NTRF': bt.ORDER,
        'NMSC': bt.ORDER,
        'NPAY': bt.PAYMENT_BATCH,
        'NCHK': bt.CHECK,
        'NCLR': bt.ORDER,
    }

    def __init__(self, record, *args, **kwargs):
        '''
        Transaction creation
        '''
        super(transaction, self).__init__(*args, **kwargs)
        for key, value in self.mapping.iteritems():
            if record.has_key(value):
                setattr(self, key, record[value])

        self.transferred_amount = record2float(record, 'amount')

        # Set the transfer type based on the bookingcode
        if record.get('bookingcode','ignore') in self.type_map:
            self.transfer_type = self.type_map[record['bookingcode']]
        else:
            # Default to the generic order, so it will be eligible for matching
            self.transfer_type = bt.ORDER

        if not self.is_valid():
            logger.info("Invalid: %s", record)
            
    def is_valid(self):
        '''
        We don't have remote_account so override base
        '''
        return (self.execution_date
                and self.transferred_amount and True) or False

class statement(models.mem_bank_statement):
    '''
    Bank statement imported data
    '''

    def import_record(self, record,**kwargs):
        def _transmission_number():
            self.id = record['transref']
        def _account_number():
            # The wizard doesn't check for sort code
            self.local_account = record['sortcode'] + record['accnum']
        def _statement_number():
            self.id = self.local_account + '-' + record['statementnr']
        def _opening_balance():
            self.start_balance = record2float(record,'startingbalance')
            self.local_currency = record['currencycode']
        def _closing_balance():
            self.end_balance = record2float(record, 'endingbalance')
            today = datetime.datetime.today() 
            dateString = today.strftime("%Y-%m-%d %H:%M:%S")
            self.id = dateString + '-' + self.id
        def _transaction_new():
            self.transactions.append(transaction(record))
        def _transaction_info():
            self.transaction_info(record)
        def _not_used():
            logger.info("Didn't use record: %s", record)
        def _forward_available():
            self.end_balance = record2float(record, 'endingbalance')
            self.date = record['bookingdate']

        rectypes = {
            '20' : _transmission_number,
            '25' : _account_number,
            '28' : _statement_number,
            '28C': _statement_number,
            '60F': _opening_balance,
            '62F': _closing_balance,
            '64' : _forward_available,
           #'62M': _interim_balance,
            '61' : _transaction_new,
            '86' : _transaction_info,
            }

        rectypes.get(record['recordid'], _not_used)()

    def transaction_info(self, record):
        '''
        Add extra information to transaction
        '''
        # Additional information for previous transaction
        if len(self.transactions) < 1:
            logger.info("Received additional information for non existent transaction:")
            logger.info(record)
        else:
            transaction = self.transactions[-1]
            #transaction.id = ','.join([record[k] for k in ['infoline{0}'.format(i) for i in range(2,5)] if record.has_key(k)])
            transaction.id = record['infoline1']    

def raise_error(message, line):
    raise osv.osv.except_osv(_('Import error'),
        _('Error in import:%s\n\n%s') % (message, line))

class parser_bac_mt940(models.parser):
    code = 'BAC-MT940'
    name = _('BAC Swift MT940 statement export')
    country_code = 'CR'
    doc = _('''\
            This format is available through
            the BAC web interface.
            ''')
    
    def parse(self, cr, statements_file,**kwargs):
        '''
            ** Kwargs parameter is used for a dynamic list of parameters. 
            The wizard imported extracts used in all parsers and not all parsers have all the necessary information in your file, 
            so get information from the wizard and passed by the ** kwargs. 
            Then in the parses that are needed, are extracted from the ** kwargs and if needed, 
            the parser still works the same way without this parameter.
            
            The rest of the methods must receive this parameter. (As the method that parse the header and the lines).
        '''
        result = []        
        parser = BACParser()
        list_record = []
        inversion_colocada = 0
        
        """
            **kwargs have all the parameters that have the wizard and 
            has all the parameters passed from the wizard before calling 
            the method that parses the file.            
        """        
        #pass to encoding with the correct type of file.        
        data = base64.decodestring(statements_file)
    
        # Split into statements
        statements = [st for st in re.split('[\r\n]*(?=:20:)', data)]
        # Split by records
        statement_list = [re.split('[\r\n ]*(?=:\d\d[\w]?:)', st) for st in statements]
        
        '''
            In the first position of the statement_list is the account number.
            If the account number that pass in the **kwargs dictionary.                
        '''
        account_number_wizard = kwargs['account_number']
        #statement_list is a list, extract the first position 
        accnum = statement_list[1][1]    
        
        #find the number in the account string.
        if accnum.find(account_number_wizard) > -1:
            for statement_lines in statement_list:
                stmnt = statement()
                
                """Data Extraction """
                for record in statement_lines:               
                    records = parser.parse_record(record,**kwargs)
    
                    if records is not None:
                        #Start PAGO CAPITAL INVERSION
                        if records['recordid'] == '60F':
                            start_balance = float(records['startingbalance'])
                        if records['recordid'] == '61':
                            amount = float(records['amount'])
                        if records['recordid'] == '86' and records['infoline1'] == 'PAGO CAPITAL INVERSION':
                            start_amount = amount
                            start_balance += amount
                        
                        #Start INVERSION COLOCADA
                        if records['recordid'] == '86':
                            cad = records['infoline1']
                            if cad.find('INVERSION COLOCADA') > 0:
                                inversion_colocada = amount
                                
                        if records['recordid'] == '62F':                                         
                            ending_balance = (inversion_colocada + float(records['endingbalance']))
    
                if records is not None:            
                    """Data Update """
                    for record in statement_lines:   
                        if record is not None:             
                            records = parser.parse_record(record)    
                    
                            if (records['recordid'] == '60F'):
                                dic = {'startingbalance':start_balance}
                                records.update(dic)
                            
                            if (records['recordid'] == '62F'):
                                dic = {'endingbalance': ending_balance}
                                records.update(dic)
    
                            if (records['recordid'] == '64'):
                                dic = {'endingbalance': ending_balance}
                                records.update(dic)
                                
                            #If the line is not a "INVERSION COLOCADA" or "PAGO CAPITAL INVERSION",
                            #it is added to the list "PAGO_CAPITAL"
                            if (records['recordid'] == '86'):
                                cad = records['infoline1']
                                
                                if (cad != "PAGO CAPITAL INVERSION") and (cad.find("INVERSION COLOCADA") < 0): 
                                    list_record.append(records)
                                    
                            if (records['recordid'] == '61'):
                                try:
                                    if float(records['amount']) != start_amount and float(records['amount']) != inversion_colocada:
                                        list_record.append(records)
                                except:
                                    list_record.append(records)
                            
                            if (records['recordid'] != '61' and records['recordid'] != '86' ):
                                list_record.append(records)                
                    
                    [stmnt.import_record(r) for r in list_record if r is not None]
                    
                    if stmnt.is_valid():
                        result.append(stmnt)
                        list_record = []
                        inversion_colocada = 0
                        start_balance = 0
                    else:
                        logger.info("Invalid Statement:")
                        logger.info(records[0])
                        logger.info(records[1])
                        logger.info(records[2])
                        logger.info(records[3])
                        logger.info(records[4])
                        list_record = []
            return result
        
        else:
            raise osv.except_osv(_('Import Error'),
                        _('The account specified in the file does not match'
                          ' the account selected in wizard.'))
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

from openerp.addons.account_banking_ccorp_dg.parsers import models
from openerp.tools.translate import _
from bcr_parser import BCRParser
import re
from openerp.osv import osv, fields
import logging
import pprint
from datetime import datetime
import base64

bt = models.mem_bank_transaction
logger = logging.getLogger( 'bcr_mt940' )

def record2float(record, value):
    if record == 'C':
        return float (value)
    else:
        return -float(value)

class transaction(models.mem_bank_transaction):

    mapping = {
        'execution_date' : '',
        'effective_date' : '',
        'local_currency' : '',
        'transfer_type' : '',
        'reference' : '',
        'message' : '',
        'name' : '',
        'amount': '',
        'creditmarker': '',
    }

    def __init__(self, record, *args, **kwargs):
        
        '''
        Transaction creation
        '''
        super(transaction, self).__init__(*args, **kwargs)
        #for r in record:
        for key, value in record.iteritems():
            if record.has_key(key):
                setattr(self, key, record[key])

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
    Bank statement imported data    '''
      
    def _transmission_number(self, record):
        self.id = record['transref']
        
    def _account_number(self, record):
        self.local_account = record['account_number']
        
    def _statement_number(self, record):
        self.id = record['id']
        
    def _opening_balance(self, record):
        self.start_balance = float(record['startingbalance'])
        self.local_currency = record['currencycode']
    
    def _closing_balance(self, record):
        self.end_balance = float(record['endingbalance'])
        self.date = record['bookingdate']
     
    def _transaction_new(self, record):
        parser = BCRParser()
        sub_record = parser.statement_lines(record) #dictionary
        for sub in sub_record:
            self.transactions.append(transaction(sub))

    def _not_used():
        logger.info("Didn't use record: %s", record)
        
    def _forward_available(self, record):
        self.end_balance =  float(record['endingbalance'])
        self.date = record['bookingdate'] 
    
    def _execution_date_transferred_amount (self, record):        
        self.execution_date = record['bookingdate']       
        self.transferred_amount = float(record['ammount'])

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
            transaction.id = ','.join([record[k] for k in ['infoline{0}'.format(i) for i in range(2,5)] if record.has_key(k)])

def raise_error(message, line):
    raise osv.osv.except_osv(_('Import error'),
        'Error in import:%s\n\n%s' % (message, line))

class parser_bcr_mt940( models.parser ):
    code = 'BCR-MT940'
    name = _( 'BCR statement import' )
    country_code = 'CR'
    doc = _('''\
            This format is available through
            the BCR  web interface.
            ''')
    
    def parse(self, cr, statements_file, **kwargs):
        
        '''
            ** Kwargs parameter is used for a dynamic list of parameters. 
            The wizard imported extracts used in all parsers and not all parsers have all the necessary information in your file, 
            so get information from the wizard and passed by the ** kwargs. 
            Then in the parses that are needed, are extracted from the ** kwargs and if needed, 
            the parser still works the same way without this parameter.
            
            The rest of the methods must receive this parameter. (As the method that parse the header and the lines).
        '''
        
        result = []
        parser = BCRParser()
        stmnt = statement()
        
        """
            **kwargs have all the parameters that have the wizard and 
            has all the parameters passed from the wizard before calling 
            the method that parses the file.            
        """        

        #pass to encoding with the correct type of file.
        data = base64.decodestring(statements_file)
    
        records = parser.parse_stamenent_record(data,**kwargs)        
        
        stmnt._transmission_number(records)
        stmnt._account_number(records)
        stmnt._statement_number(records)
        stmnt._opening_balance(records)
        stmnt._closing_balance(records)
        stmnt._forward_available(records)
        stmnt._execution_date_transferred_amount (records)
        stmnt._transaction_new(data)
                  
        if stmnt.is_valid():
            result.append(stmnt)
            
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

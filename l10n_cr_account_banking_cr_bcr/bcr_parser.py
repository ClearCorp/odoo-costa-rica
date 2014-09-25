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
"""
Parser for BCR format files
"""
import re
from datetime import datetime
from dateutil import parser
from pprint import PrettyPrinter
from copy import copy
from openerp.tools.translate import _
from openerp.osv import osv, fields

class BCRParser( object ):
    """
    BCR Parser object is intended to parse bank statements files 
    from raw files. Constant changes in raw files are forcing this
    module to keep in constant revision due to an external situation 
    """
    
    def statement_record ( self, rec, **kwargs):
        lines = []
        line_dict = {}

        line_dict = {
            'transref': 0.0, # _transmission_number
            'account_number': '', #_account_number
            'statementnr':'', # statement_number
            'startingbalance': 0.0, #_opening_balance
            'currencycode': 'CRC', #currencycode
            'endingbalance': 0.0, #_closing_balance
            'bookingdate': '', #moving_date
            'ammount': 0.0,
            'id': '',
        }

        cad = ''
        list_split = rec.split('\r\n')
        account_number_wizard = kwargs['account_number']

        #If return True, the account are the same.
        if self.match_account(list_split, account_number_wizard):        
            for l in list_split:                
                #_account_number -> FIRST REVISION
                if l.find('Movimiento de Cuenta Corriente', 0, len('Movimiento de Cuenta Corriente')) > -1:
                    line_dict['account_number'] = self.extract_number(l)                
                    
                    if (l.find('D',0,len(l)) > -1):
                        line_dict['currencycode'] = 'USD'
                    else:
                        line_dict['currencycode'] = 'CRC'
                        
                #_account_number -> SECOND REVISION        
                elif (l.find('MOVIMIENTO DE LA CUENTA  CORRIENTE No.', 0, len('MOVIMIENTO DE LA CUENTA  CORRIENTE No.')) > -1):
                    line_dict['account_number'] = self.extract_accnumber(l)
                    if (l.find('DOLARES',0,len(l)) > -1):
                        line_dict['currencycode'] = 'USD'
                    else:
                        line_dict['currencycode'] = 'CRC'
                
                # _transmission_number -> FIRST REVISION
                if (l.find('Movimiento realizado el periodo', 0, len('Movimiento realizado el periodo')) > -1):
                    line_dict['statementnr'] = self.extract_number(l)
                    date_1 = self.extract_date_regular_expresion_line_format_2(l,0)
                    date_2 = self.extract_date_regular_expresion_line_format_2(l,1)
                
                # _transmission_number -> SECOND REVISION
                elif (l.find('MOVIMIENTO REALIZADO', 0, len('MOVIMIENTO REALIZADO')) > -1):
                    line_dict['statementnr'] = self.extract_number(l)
                    date_1 = self.extract_date_regular_expresion_line_format_2(l,0)
                    date_2 = self.extract_date_regular_expresion_line_format_2(l,1)
                       
                #date and hour -> FIRST REVISION 
                if (l.find('Movimiento realizado', 0, len('Movimiento realizado'))  > -1):
                    date =  hour = cad = ''
                    date = self.extract_date_regular_expresion(l)
                    if len(date) > 0:                   
                        hour = '00:00:00'
                    cad = date + ' ' + hour
                    line_dict['transref'] = cad
                    line_dict['bookingdate'] = cad
                
                #date and hour -> SECOND REVISION                 
                elif (l.find('MOVIMIENTO REALIZADO', 0, len('MOVIMIENTO REALIZADO'))  > -1):
                    date =  hour = cad = ''
                    date = self.extract_date_regular_expresion(l)
                    if len(date) > 0:                   
                        hour = "00:00:00"
                    cad = date + ' ' + hour
                    line_dict['transref'] = cad
                    line_dict['bookingdate'] = cad
                                   
                #_opening_balance -> FIRST REVISION
                if l.find('Saldo Inicial', 0, len('Saldo Inicial'))  > -1:
                    line_dict['startingbalance'] = self.extract_float(l)
                #_opening_balance -> SECOND REVISION   
                elif l.find('INICIAL', 0, len('INICIAL'))  > -1:
                    line_dict['startingbalance'] = self.extract_float(l)
                        
                #_closing_balance -> FIRST REVISION
                if l.find('DISPONIBLE', 0, len('DISPONIBLE'))  > -1:
                    line_dict['endingbalance'] = self.extract_float(l)
              
                #_closing_balance -> SECOND REVISION    
                elif l.find('Saldo Final', 0, len('Saldo Final'))  > -1 or l.find('FINAL', 0, len('FINAL'))  > -1:
                    line_dict['endingbalance'] = self.extract_float(l)
                        
            line_dict['ammount'] = float( line_dict['startingbalance'] ) + float( line_dict['endingbalance'] )
            line_dict['id'] = date_1 + ' - ' + date_2 + ' Extracto BCR ' + line_dict['account_number']
            self.line_dict = line_dict
          
            return line_dict
        
        else:
            raise osv.except_osv(_('Error'),
                        _('Error during import. The account specified in the file'
                          ' does not match the account selected in wizard'))
        
    def statement_lines ( self, rec):
        parser = BCRParser()
        mapping = {
            'execution_date' : '',
            'effective_date' : '',
            'local_currency' : '',
            'transfer_type' : '',
            'reference' : '',
            'message' : '',
            'name' : '',
            'transferred_amount': '',
            'creditmarker': '',
        }
        line_dict = {}
        currencycode = ''
        
        list_split = rec.split('\r\n')
        entrada = False
        start = 0
        end = 0
        version = 'none'
        
        #========= Start and end of lines ======#
        for l in list_split: 
            if l.find('TOTALES DEL MOVIMIENTO CONTABILIZADO', 0, len('TOTALES DEL MOVIMIENTO CONTABILIZADO')) <= -1:
                end += 1
            else:
                break                
        end = end - 1
        
        for l in list_split:           
            if l.find('-CONTABLE-', 0, len('-CONTABLE-')) <= -1:
                start += 1
            else:
                break
        start += 1 
        
        for l in list_split:           
            if l.find('Movimiento de Cuenta Corriente', 0, len('Movimiento de Cuenta Corriente')) > -1:
                if (l.find('D',0,len(l)) > -1):
                    currencycode = 'USD'
                else:
                    currencycode = 'CRC'
                break
            
            elif l.find('MOVIMIENTO DE LA CUENTA  CORRIENTE No.', 0, len('MOVIMIENTO DE LA CUENTA  CORRIENTE No.')) > -1:
                if (l.find('DOLARES',0,len(l)) > -1):
                    currencycode = 'USD'
                else:
                    currencycode = 'CRC'
                break            
        
        #========= VERSION OF THREE COLUMNS FOR DEBIT AND CREDIT =============# 
        sub_list = list_split [start:end]
        
        if len(sub_list) > 0:
            sub_first = sub_list[0] #Based in first line, decide which version it is
            
            #1. Try separate by tab ('\t') (last version) (fields must have, at least, more than 1 of length)
            fields = sub_first.split('\t')
            
            if len(fields) > 1:
                version = 'third_version'
            
            #2. Find where start debit and credit columns
            else:
                amount = sub_first[106:]
                debit = amount[0:16]
                
                debit = debit.replace(',','')
                debit = debit.replace('.','')
                debit = re.sub(r'\s', '', debit)
                
                if re.match('^[0-9,.]*$', debit):
                    version = 'first_version'
                
                else:
                    amount = sub_first[120:]            
                    debit = amount[0:40]
                    
                    debit = debit.replace(',','')
                    debit = debit.replace('.','')
                    debit = re.sub(r'\s', '', debit)
                    
                    if re.match('^[0-9,.]*$', debit):
                        version = 'second_version'
                        
            #=====================================================================#
            
            if version != 'none':
                if version =='first_version':
                    return self.first_version_file(sub_list,mapping,currencycode,parser)
                
                elif version == 'second_version':
                    return self.second_version(sub_list,mapping,currencycode,parser)
                
                elif version == 'third_version':
                    return self.third_version(sub_list,mapping,currencycode,parser)
                        
            else:
                raise osv.except_osv(_('Error'),
                                     _('There is not format implementend for this file.'))
            
        else:
            return []    
    
    def parse_stamenent_record( self, rec, **kwargs):

        matchdict = dict()

        matchdict = self.statement_record( rec, **kwargs );

        # Remove members set to None
        matchdict = dict( [( k, v ) for k, v in matchdict.iteritems() if v] )

        matchkeys = set( matchdict.keys() )
        needstrip = set( [ 'transref', 'account_number', 'statementnr', 'currencycode', 'endingbalance', 'bookingdate'] )

        for field in matchkeys & needstrip:
            matchdict[field] = matchdict[field].strip()

        # Convert to float. Comma is decimal separator
        needsfloat = set( ["startingbalance", "endingbalance", "amount"] )
        for field in matchkeys & needsfloat:
            matchdict[field] = float( matchdict[field].replace( ',', '.' ) )

        # Convert date fields
        needdate = set( ["bookingdate"] )
                
        for field in matchkeys & needdate:            
            datestring = matchdict[field]
            date = self.extract_date_regular_expresion(datestring)
            hour = self.extract_hour_regular_expresion(datestring)
            
            date_complete = date + ' ' + hour
            try:
                #FORMAT DATE REVISION # 1
                date_obj= datetime.strptime(date_complete, "%d/%m/%Y %H:%M:%S")
            except:
                #FORMAT DATE REVISION # 2
                date_obj= datetime.strptime(date_complete, "%d-%m-%Y %H:%M:%S")
            matchdict[field] = date_obj
        
        return matchdict
    
    #=============================Auxiliary methods =============================#
    
    #=====================Versions of file
    
    def first_version_file(self, sub_list,mapping,currencycode,parser):
        lines = []
        for sub in sub_list:
            #effective_date
            date_str = ''
            date_str = self.extract_date_regular_expresion_line(sub,0)
            date= datetime.strptime(date_str, "%d-%m-%y")               
            mapping['effective_date'] = date #fecha_contable.
            
            #execution_date
            date_str = self.extract_date_regular_expresion_line(sub,1)
            date = datetime.strptime(date_str, "%d-%m-%y")
            mapping['execution_date'] = date #fecha_movimiento                       
           
            mapping['local_currency'] = currencycode
            mapping['transfer_type'] = 'NTRF'
            mapping['reference'] = parser.extract_number(sub[18:26])
            mapping['message'] = sub[27:80]                
            mapping['name'] = sub[27:80]
            mapping['id'] = sub[27:80]
            
            amount = sub[106:]
            amount.replace('\t',' ')
            debit = amount[0:16]
            credit = amount[16:]
            
            if (parser.extract_float(debit) is not ''): #debit
                cad = parser.extract_float(debit)
                mapping['transferred_amount'] = -float(cad)      
                mapping['creditmarker'] = 'C'
                                      
            else: #credit
                cad = parser.extract_float (credit)
                mapping['transferred_amount'] =  float(cad)
            
            if not mapping['transferred_amount'] == 0.0:
                lines.append(copy(mapping))
                            
        return lines
    
    def second_version (self, sub_list,mapping,currencycode,parser):
        lines = []
        for sub in sub_list:
            #effective_date
            date_str = ''
            date_str = self.extract_date_regular_expresion_line(sub,0)
            date= datetime.strptime(date_str, "%d-%m-%y")               
            mapping['effective_date'] = date #fecha_contable.
            
            #execution_date
            date_str = self.extract_date_regular_expresion_line(sub,1)
            date = datetime.strptime(date_str, "%d-%m-%y")
            mapping['execution_date'] = date #fecha_movimiento                       
           
            mapping['local_currency'] = currencycode
            mapping['transfer_type'] = 'NTRF'
            mapping['reference'] = parser.extract_number(sub[18:26])
            mapping['message'] = sub[27:80]                
            mapping['name'] = sub[27:80]
            mapping['id'] = sub[27:80]
            
            amount = sub[120:]
            amount.replace('\t',' ')
            debit = amount[0:40]
            credit = amount[40:]
            
            if (parser.extract_float(debit) is not ''): #debit
                cad = parser.extract_float(debit)
                mapping['transferred_amount'] = -float(cad)      
                mapping['creditmarker'] = 'C'
                                      
            else: #credit
                cad = parser.extract_float (credit)
                mapping['transferred_amount'] =  float(cad)
            
            if not mapping['transferred_amount'] == 0.0:
                lines.append(copy(mapping))
                            
        return lines    
    
    def third_version(self, sub_list,mapping,currencycode,parser):
        lines = []
        for l in sub_list:
            fields = l.split('\t')
            
            #effective_date
            date_str = fields[0]
            date= datetime.strptime(date_str, "%d-%m-%y")               
            mapping['effective_date'] = date #fecha_contable.
            
            #execution_date
            date_str = fields[1]
            date = datetime.strptime(date_str, "%d-%m-%y")
            mapping['execution_date'] = date
            mapping['local_currency'] = currencycode
            mapping['transfer_type'] = 'NTRF'
            mapping['reference'] = parser.extract_number(fields[2])
            mapping['message'] = fields[3]                
            mapping['name'] = fields[3]
            mapping['id'] = fields[3]
            
            #Extract debit and credit
            if not fields[5].strip() and not fields[6].strip():
                continue
            debit = fields[5]
            if (parser.extract_float(debit) is not ''): #debit
                cad = parser.extract_float(debit)
                mapping['transferred_amount'] = -float(cad)      
                mapping['creditmarker'] = 'C'
                                      
            else: #credit
                credit = fields[6]
                cad = parser.extract_float(credit)
                mapping['transferred_amount'] =  float(cad)
            
            if not mapping['transferred_amount'] == 0.0:
                lines.append(copy(mapping))
        
        return lines
        
    #===============================================================                
    def extract_number( self, account_number ):
        cad = ''
        result = re.findall(r'[0-9]+', account_number)
               
        for character in result:
            cad = cad + character
        return cad
    
    def extract_accnumber(self, line):
        cad = ''
        result = re.findall(r'[0-9-]+', line)
               
        for character in result:
            cad = cad + character
        return cad
        

    def extract_float ( self, amount ):
        cad = ''
        result = re.findall(r"[-+]?\d*\.\d+|\d+",amount)
        
        for character in result:
            cad = cad + character       
        return cad
    
    def extract_date_regular_expresion(self, date):
        cad = ''
        result = []
        date_string = ''
        #re.findall('[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}',str)[0]+' '+re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}',str)[0]
        #FORMAT DATE FIRST REVISION
        result = re.findall('[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}', date)
       
        if len(result) == 0:
            #FORMAT DATE SECOND REVISION
            result = re.findall('[0-9]{1,2}-[0-9]{1,2}-[0-9]{4}',date)      
        
        if result:
            cad = result[0]
        return cad
    
    #with the pos parameter is said which of the two dates must be brought
    #result brings a list of two elements, the post tells us to choose    
    def extract_date_regular_expresion_line(self, date, pos):
        cad = ''
        result = []
        date_string = ''
        result = re.findall('([0-9]{2}-[0-9]{2}-[0-9]{2})[\s]*',date)      
        date_str = result[pos]
        
        for character in date_str:
            cad = cad + character       
        return cad
    
    #with the pos parameter is said which of the two dates must be brought
    #result brings a list of two elements, the post tells us to choose    
    def extract_date_regular_expresion_line_format_2(self, date, pos):
        cad = ''
        result = []
        date_string = ''
        result = re.findall('([0-9]{2}-[0-9]{2}-[0-9]{4})[\s]*',date)      
        date_str = result[pos]
        
        for character in date_str:
            cad = cad + character       
        return cad
    
    def extract_hour_regular_expresion(self, date):
        cad = ''
        result = []

        result = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}',date)             
        
        for character in result:
            cad = cad + character       
        return cad

    def extract_currency_code_USD(self, currency):
        cad = ''
        result = re.findall('[D.lares]',currency)
        for character in result:
            cad = cad + character
        return cad

    def parse( self, cr, data ):
        records = []
        # Some records are multiline
        for line in data:
            if len(line) <= 1:
                continue
            if line[0] == ':' and len(line) > 1:
                records.append(line)
            else:
                records[-1] = '\n'.join([records[-1], line])
                
        output = []

        for rec in records:
            output.append( self.parse_stamenent_record( rec ) )
                
        return output
    
    #check if the account_number in the file match with the selected in the wizard.
    def match_account(self, list_split, account_number_wizard):
        accnumber = ''
        for l in list_split:            
             #_account_number -> FIRST REVISION
            if l.find('Movimiento de Cuenta Corriente', 0, len('Movimiento de Cuenta Corriente')) > -1:
                accnumber = self.extract_number(l)                
                break
            
             #_account_number -> SECOND REVISION        
            elif (l.find('MOVIMIENTO DE LA CUENTA  CORRIENTE No.', 0, len('MOVIMIENTO DE LA CUENTA  CORRIENTE No.')) > -1):
                accnumber = self.extract_number(l)
                break
        
        #If return True, the account_number in the wizard and the account in the file are the same.
        if accnumber.find(account_number_wizard) > -1:
            return True
        else:
            return False
    

def parse_file( filename ):
    bacfile = open( filename, "r" )
    p = BCRParser().parse(bacfile.readlines())

def main():
    """The main function, currently just calls a dummy filename

    :returns: description
    """
    parse_file("testfile")

if __name__ == '__main__':
    main()


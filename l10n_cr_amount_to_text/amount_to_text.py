# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)

UNITS = (
    '',
    'UN ',
    'DOS ',
    'TRES ',
    'CUATRO ',
    'CINCO ',
    'SEIS ',
    'SIETE ',
    'OCHO ',
    'NUEVE ',
    'DIEZ ',
    'ONCE ',
    'DOCE ',
    'TRECE ',
    'CATORCE ',
    'QUINCE ',
    'DIECISEIS ',
    'DIECISIETE ',
    'DIECIOCHO ',
    'DIECINUEVE ',
    'VEINTE '
)

TENS = (
    'VENTI',
    'TREINTA ',
    'CUARENTA ',
    'CINCUENTA ',
    'SESENTA ',
    'SETENTA ',
    'OCHENTA ',
    'NOVENTA ',
    'CIEN ',
)

HUNDREDS = (
    'CIENTO ',
    'DOSCIENTOS ',
    'TRESCIENTOS ',
    'CUATROCIENTOS ',
    'QUINIENTOS ',
    'SEISCIENTOS ',
    'SETECIENTOS ',
    'OCHOCIENTOS ',
    'NOVECIENTOS ',
)


# TODO: Remove currency param
def number_to_text_es(number_in, currency, join_dec=' Y ',
                      separator=',', decimal_point='.'):
    converted = ''
    if currency is False or currency is None:
        currency = ''

    # Check type and convert to str
    if type(number_in) != 'str':
        number = str(number_in)
    else:
        number = number_in

    # Remove the separator from the string
    try:
        number = number.replace(separator, '')
    except ValueError:
        _logger.info("An error occurred while replacing the "
                     "separator an error may occur.")

    # Get the integer and decimal part of the numbers
    try:
        number_int, number_dec = number.split(decimal_point)
    except ValueError:
        number_int = number
        number_dec = ""
        _logger.info("No decimal part found on the number.")

    number = number_int.zfill(9)
    millions = number[:3]
    thousands = number[3:6]
    hundreds = number[6:]

    if millions:
        if millions == '001':
            converted += 'UN MILLON '
        elif int(millions) > 0:
            converted += '%sMILLONES ' % _convert_number(millions)

    if thousands:
        if thousands == '001':
            converted += 'MIL '
        elif int(thousands) > 0:
            converted += '%sMIL ' % _convert_number(thousands)

    if hundreds:
        if hundreds == '001':
            converted += 'UN '
        elif int(hundreds) > 0:
            converted += '%s ' % _convert_number(hundreds)

    if number_dec == "":
        number_dec = "00"
    if len(number_dec) < 2:
        number_dec += '0'

    # TODO: Check currency inclusion
    has_decimal = float(number_dec) != 0 and join_dec + number_dec +\
        "/100" or ' EXACTOS'
    converted += currency + has_decimal

    return converted


def _convert_number(n):
    output = ''

    if n == '100':
        output = "CIEN "
    elif n[0] != '0':
        output = HUNDREDS[int(n[0])-1]

    k = int(n[1:])
    if k <= 20:
        output += UNITS[k]
    else:
        if (k > 30) & (n[2] != '0'):
            output += '%sY %s' % (TENS[int(n[1])-2], UNITS[int(n[2])])
        else:
            output += '%s%s' % (TENS[int(n[1])-2], UNITS[int(n[2])])

    return output

import os
import csv

columns = {
  0: 'CodeNum',
  1: 'Code',
  2: 'Glyph',
  3: 'Decimal',
  4: 'HTML',
  5: 'Description',
  6: 'Extra',
}

headerRows = 2

def debug(str, debug=False):
  if debug:
    print(str)

file = open('escape_characters.csv')
csv_file = csv.reader(file)

for row_num, csv_row in enumerate(csv_file):
  row_values={}
  if((row_num > headerRows) and (row_num < 100)): 
    debug("---------------------------------------------")
    debug(row_num)
    for column_num, column_value in enumerate(csv_row):
      if(columns[column_num] == 'Decimal'):
        code_num = csv_row[0]
        code_decimal = int(code_num,16)
        row_values[column_num] = code_decimal

      else:
        row_values[column_num] = csv_row[column_num] 
        pass

    #print(row_values[0],row_values[3], row_values[5])
    val = str(row_values[3]) + " "
    print(val, end = ', ')

debug("Decimal: ")

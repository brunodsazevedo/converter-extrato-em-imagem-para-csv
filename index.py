from PIL import Image
from collections import namedtuple
import re
import pytesseract
import pandas as pd

file = Image.open('extrato.jpg')

Bank_Transactions = namedtuple('Line', 'dt_movimento historico valor d_c')
Line_Date_History = namedtuple('Line_Date_History', 'dt_movimento, historico')
Line_value = namedtuple('Line_value', 'valor d_c')

date_history_re = re.compile(r'(\d+\/\d+\/\d+)(?:\s)(?:\d+)(?:\s)(?:\d+)(?:\s)(.*)')
continuous_history_re = re.compile(r'^\d+\/\d+\/\d+')
value_re = re.compile(r'^(\d+\,\d+|\d+\.\d+\,\d+|\d+\,\d+)(?:\s)(D|C)|(\d+\,\d+|\d+\.\d+\,\d+|\d+\,\d+)(D|C)|(\d+)(D|C)')

bank_statement = pytesseract.image_to_string(file, lang='por')

list_bank_statement = []
list_values_transictions = []
list_date_history = []

is_value = False
is_balance = False

for line in bank_statement.split('\n'):
    print(line)
    
    if line == 'Valor R$':
        is_value = True
        is_balance = False
        
    if line == 'Saldo':
        is_value = False
        is_balance = True
        
    search_value = value_re.search(line)
    if search_value and is_value == True:
        if search_value.group(1) and search_value.group(2):
            value, d_c = search_value.group(1), search_value.group(2)
        if search_value.group(3) and search_value.group(4):
            value, d_c = search_value.group(3), search_value.group(4)
        if search_value.group(5) and search_value.group(6):
            value, d_c = search_value.group(5), search_value.group(6)
            
        list_values_transictions.append(Line_value(value, d_c))
    
    search_bank_transaction = date_history_re.search(line)
    if search_bank_transaction and is_value == False and is_balance ==False :
        date, history = search_bank_transaction.group(1), search_bank_transaction.group(2)
        list_date_history.append(Line_Date_History(date, history))

key_list_values_transictions = 0
key_list_date_history = 0

while key_list_date_history < len(list_date_history):
    
    if list_date_history[key_list_date_history][1] != '000 Saldo Anterior':
        dt_movimento = list_date_history[key_list_date_history][0]
        historico = list_date_history[key_list_date_history][1]
        
        valor = list_values_transictions[key_list_values_transictions][0]
        d_c = list_values_transictions[key_list_values_transictions][1]
        
        list_bank_statement.append(Bank_Transactions(dt_movimento, historico, valor, d_c))

        key_list_values_transictions += 1
    
    key_list_date_history += 1


data_frame = pd.DataFrame(list_bank_statement)

data_frame.head()
data_frame.info()

data_frame.to_csv('extrato.csv', index=False)

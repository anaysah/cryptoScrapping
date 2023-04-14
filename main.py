import requests
from bs4 import BeautifulSoup
import mysql.connector

#url of crypto website
url = 'https://crypto.com/price'

#---Get the data from website
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

#---Extract the headers from table
table = soup.find('table', {'class': 'chakra-table css-1qpk7f7'})
header_row = table.find('thead').find('tr')
headers = [header.text.strip() for header in header_row.find_all('th')]
headers = headers[2:-2]

#---Extract the all rows of data from table
data_rows = table.find('tbody').find_all('tr')
data = []

for row in data_rows:
    cells = row.find_all('td')
    row_data = {}
    for cell, n in zip(cells[2:-2], range(len(headers))):
        text = cell.text.strip()
        if(n==1):
            #To get only numbers of the string value in price like($30,844.34==30,844.34)
            text = cell.text.strip().split("$")[1]
        elif(n==0):
            #To get code name and the full name of the crypto
            text = cell.find('p',{'class','chakra-text css-rkws3'}).text.strip()
            row_data['code'] = cell.find('span',{'class','chakra-text css-1jj7b1a'}).text.strip()
        elif(n==4):
            #To get only numbers of the string value in market_cap like($596.69 B==596.69)
            text = cell.text.strip().split()[0].split("$")[1]
        row_data[headers[n]] = text
        
    data.append(row_data)


#---Creating database named crypto
cnx = mysql.connector.connect(user='root', password='',
                              host='localhost')
cursor = cnx.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS crypto")
cursor.execute("use crypto")

#---If the cryptocurrencies table already exists then delete it and create a new one
table_name = "cryptocurrencies"
cursor.execute("SHOW TABLES LIKE '{}'".format(table_name))
result = cursor.fetchone()

if result:
    cursor.execute("DROP TABLE {}".format(table_name))
    print("Table {} dropped successfully.".format(table_name))
else:
    print("Table {} does not exist.".format(table_name))

create_table_sql = '''
CREATE TABLE cryptocurrencies (
    code VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    price_$ DECIMAL(10,2) NOT NULL,
    change_24h VARCHAR(255) NOT NULL,
    volume_24h VARCHAR(255) NOT NULL,
    market_cap_Billion$ DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (code)
)
'''
cursor.execute(create_table_sql)


#---Inserting the data into the newlly created table cryptocurrencies
insert_sql = '''
INSERT INTO cryptocurrencies
VALUES (%s, %s, %s, %s, %s, %s)
'''

for row in data:
    #changing the string into the float by removing comma
    price = row['Price'].replace(",","")
    market_cap = row['Market Cap'].replace(",","")
    values = (row['code'],row['Name'],float(price),row['24H CHANGE'], row['24H VOLUME'], float(market_cap))
    print(values)
    cursor.execute(insert_sql, values)

cnx.commit()
cursor.close()
cnx.close()


#Note: the price and market_cap is only stored as a decimal in the database for better understanding
#24H_change is a negative or positive percent value and it can be further divided into two columns but not done in this code
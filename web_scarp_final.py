import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
import os.path
import schedule
import time

# Android 9 with Google Chrome
user_agent_smartphone = 'Mozilla/5.0 (Linux; Android 9; SM-G960F '\
'Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) '\
'Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36'

headers = {'User-Agent': user_agent_smartphone}

url = 'https://www.theverge.com' # website from which scraping done.

def scrap():
    resp = requests.get(url)  # Send request to the url
    resp = requests.get(resp.url, headers=headers) # Send request with updated link to the url
    code = resp.status_code  # HTTP response code

    if code == 200: #The HTTP 200, OK success status response code indicates that the request has succeeded
        print('URL loaded successfully \n')
        soup=BeautifulSoup(resp.text, 'lxml')#creating a soup object.
        element=soup.find_all("div", {"class": "c-entry-box--compact__body"})


        #-----------------------connection---------------------
        try:
            sqliteConnection = sqlite3.connect('sqlite_data.db')# conncting to the DB
            cursor = sqliteConnection.cursor() #couser object for Executing sql lite Statement.

            # print("Database created and Successfully Connected to SQLite")
            try:
                # statement for creating Table.
                query = '''CREATE TABLE articles (  id INTEGER PRIMARY KEY, 
                                                    url VARCHAR(2048) UNIQUE,
                                                    title VARCHAR(500),
                                                    author VARCHAR(100),
                                                    date date);'''
                cursor.execute(query)#Executing the Query for creating table.
            except:
                print('Table alredy exists, program continues...')
        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)

        cursor.execute("SELECT * FROM articles")
        k=len(cursor.fetchall())
        data=[]
        for e in element:
            try:
                #inserting data into database from website.
                query = f'''INSERT INTO articles VALUES ({k}, '{e.h2.a['href']}', '{e.h2.a.text}', '{e.div.a.text}', date('{e.h2.a['href'][25:33]}'));'''
                cursor.execute(query)
                #Inserting data into a list.
                dic={'id': k, 'url': e.h2.a['href'], 'title': e.h2.a.text, 'author': e.div.a.text, 'date': e.h2.a['href'][25:33]}
                data.append(dic)
            except:
                print('duplicate found, not inserted.')
            sqliteConnection.commit()
            k+=1
#closing all resources manually.
        cursor.close()
        sqliteConnection.close()


        #-------------------CSV Write----------------------------------
        field_names= ['id', 'url', 'title', 'author', 'date']
        with open('data.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            if not os.path.isfile('data.csv'):
                writer.writeheader()
            writer.writerows(data)
            csvfile.close()

    else:
        print('Error to load the URL:', code)


#----------------Run code daily at 00:00-----------------

schedule.every().day.at("00:00").do(scrap)

# schedule.every().day.at("20:00").do(scrap)

while True:
    schedule.run_pending()
    time.sleep(1)



#----------------Print database--------------------------
# sqliteConnection = sqlite3.connect('sqlite_data.db')
# cursor = sqliteConnection.cursor()
# cursor.execute("SELECT * FROM articles")
# record = cursor.fetchall()
# print("Data is: ", record[-1])
# print("No of rows is: ", len(record))
# cursor.close()
# sqliteConnection.close()
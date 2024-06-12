from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import csv
import sys
import mysql.connector
from plyer import notification
import requests
from bs4 import BeautifulSoup



url="https://www.pesuacademy.com/Academy/getStudentClassInfo"

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Csrf-Token': 'ab8cc7f1-6679-436c-9615-fd5bb9287be0',
    'Accept': '*/*',
    'Cookie': 'JSESSIONID=qGDc0PPyX34l6hH1D0rsDLg59wB0wPtyjEm82_Lk.ip-172-21-1-74; AWSALB=5jRxerNt09EuKpnlh0KqPJQXYc/hTdFzAmOLOMgxez4Zg9qQrftLdePf/3soeL0CR5Ed6TF6rsBZ1O1pQr1gJUeGRkrgTdScrBFRI+r+3YwaPgXGEQQs8Fy/QqYt; AWSALBCORS=5jRxerNt09EuKpnlh0KqPJQXYc/hTdFzAmOLOMgxez4Zg9qQrftLdePf/3soeL0CR5Ed6TF6rsBZ1O1pQr1gJUeGRkrgTdScrBFRI+r+3YwaPgXGEQQs8Fy/QqYt',
    'Origin': 'https://www.pesuacademy.com',
    'Referer': 'https://www.pesuacademy.com/Academy/',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',

}

branch = sys.argv[1]
year = sys.argv[2]
if (branch == "ec"):
    st = "PES2"
else:
    st = "PES1"


print("Running")
fileName = "batch_of_" + year + "_prn_to_srn.csv"
f = open(fileName, "a")
f1 = open("errors.txt", "a")
print("Files created")


database = mysql.connector.connect(
    user='pes_people_bot',
    password='super_secure_password',
    host='localhost',
    database='prn_to_srn'
)

print("db connected")
cursor = database.cursor()


# cursor.execute("drop table if exists THETABLE")
cursor.execute("create table if not exists THETABLE (PRN varchar(15), SRN varchar(15))")


for i in range(0, 8000):
    if (i >= 1 and i <= 9):
        s = "000" + str(i)
    elif (i >= 10 and i <= 99):
        s = "00" + str(i)
    elif (i >= 100 and i <= 999):
        s = "0" + str(i)
    else:
        s = str(i)
    try:
        
        inputPRN = st + year + "0" + s
        data = {
            'loginId': inputPRN
        }
        response = requests.post(url, headers=headers, data=data)
        response_text = response.text
        soup = BeautifulSoup(response_text, 'html.parser')

        try:
            tbody = soup.find('tbody', {'id': 'knowClsSectionModalTableDate'})
        except Exception as e:
        # When class and section is not found, the response is some bs that says 'class and section details are not available'
        # no table is returned in this case. So the above statement would throw an error. If this is the case, we can move on from this PRN
            continue
        first_row = tbody.find('tr')

        srn_cell = first_row.find_all('td')[1]

        srn = srn_cell.text

        if(srn == "NA"):
            print("Skipping " + inputPRN)
            continue
        strRow = inputPRN + "," + srn
        print("Got for", inputPRN)

        f.write(strRow + "\n")


        query = f"insert into THETABLE values ('{inputPRN}', '{srn}')"
        cursor.execute(query)
        database.commit()
    except Exception as e:
        f1.write(inputPRN+"\n")
        print(inputPRN, "error", e)
f.close()
f1.close()
print("File closed")
print("Browser closed")
database.close()
print("db closed")
notification.notify(
    title = 'Scraper Bot',
    message = 'Finished the task',
    app_icon = None,
    timeout = 15,
)

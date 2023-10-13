from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import csv
import sys
import mysql.connector
from plyer import notification

campus = sys.argv[1]
year = sys.argv[2]
if (campus == "ec"):
    campusCode = "PES2"
else:
    campusCode = "PES1"


print("Running")
opts = Options()
opts.headless = True
browser = Firefox(options=opts)
print("Browser running")
fName = "batch_of_" + year + ".csv"
f = open(fName, "a")
f1 = open("errors.txt", "a")
print("Files created")


database = mysql.connector.connect(
    user='pes_people_bot',
    password='super_secure_password',
    host='localhost',
    database='pes_people'
)

print("db connected")
cursor = database.cursor()


cursor.execute("show tables")
show_tables_query = cursor.fetchall()
classes_already_in_db = [table[0] for table in show_tables_query]
print(classes_already_in_db)


for i in range(1, 4000):
    if (i >= 1 and i <= 9):
        studentId = "000" + str(i)
    elif (i >= 10 and i <= 99):
        studentId = "00" + str(i)
    elif (i >= 100 and i <= 999):
        studentId = "0" + str(i)
    else:
        studentId = str(i)
    browser.get('https://pesuacademy.com')
    sleep(2)
    browser.find_element(By.ID, "knowClsSection").click()
    inp = browser.find_element(By.ID, "knowClsSectionModalLoginId")
    inputPRN = campusCode + year + "0" + studentId
    inp.send_keys(inputPRN)
    try:
        browser.find_element(By.ID, "knowClsSectionModalSearch").click()
        sleep(1)
        semValue = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[4]").text

        strCamp = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[7]").text

        campus = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[9]").text

        section = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[5]").text
        if ("CIE" in semValue):
            semValue = browser.find_element(
                By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr[2]/td[4]").text
            strCamp = browser.find_element(
                By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr[2]/td[7]").text
            campus = browser.find_element(
                By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr[2]/td[9]").text
            section = browser.find_element(
                By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr[2]/td[5]").text
        prn = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[1]").text
        srn = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[2]").text
        # semValue = browser.find_element(By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[4]").text
        cycle = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[6]").text
        stream = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[8]").text
        name = browser.find_element(
            By.XPATH, "//*[@id='knowClsSectionModalTableDate']/tr/td[3]").text
        strRow = prn + "," + srn + "," + semValue + "," + section + "," + \
            cycle + "," + strCamp + "," + stream + "," + campus + "," + name
        print("Got for", prn)

        f.write(strRow + "\n")

        clas = (semValue+"_"+strCamp+"_"+section+"_"+cycle).replace(" ", "_")
        clas = clas.replace("-", "_")
        clas = clas.replace("(", "")
        clas = clas.replace(")", "")
        clas = clas.replace(".", "")
        clas = clas.replace("&", "and")

        if clas not in classes_already_in_db:
            classes_already_in_db.append(clas)
            query = f"create table {clas}(PRN varchar(32), SRN varchar(32), Name varchar(64))"
            print(query)
            cursor.execute(query)
            print(f"created table {clas}")

        query = f"insert into {clas} values ('{prn}', '{srn}', '{name}')"
        print(query)
        cursor.execute(query)
        database.commit()

    except Exception as e:
        f1.write(inputPRN+"\n")
        print(inputPRN, "error", e)
f.close()
f1.close()
print("File closed")
browser.close()
print("Browser closed")
database.close()
print("db closed")

notification.notify(
    title = 'Scraper Bot',
    message = 'Finished the task',
    app_icon = None,
    timeout = 15,
)

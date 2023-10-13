from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import csv
import sys
import mysql.connector
from plyer import notification
from telegram import Update
from telegram.ext import (
Application,
CallbackContext,
CommandHandler,
MessageHandler,
filters
)

c = sys.argv[0]
yr = sys.argv[0]
if (c == "ec"):
    st = "PES2"
else:
    st = "PES1"


# notification.notify(
#     title = "redirect",
#     message = 'You are being redirected to the telegram bot',
#     timeout = 5

application = Application.builder().token("YOUR API TOKEN HERE").build()
print("Successfully connected to Telegram API")
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am a bot that is going to mimic you :)")

print("Running")
opts = Options()
opts.headless = True
browser = Firefox(options=opts)
print("Browser running")
name = "batch_of_" + yr + ".csv"
print(name)

f1 = open("errors.txt", "a")
print("Files created")


database = mysql.connector.connect(
    user='root@localhost',
    password='abcd',
    host='localhost',
    database='ded'
)

print("db connected")
cursor = database.cursor()


cursor.execute("show tables")
show_tables_query = cursor.fetchall()
classes_already_in_db = [table[0] for table in show_tables_query]
print(classes_already_in_db)


for i in range(1, 4000):
    if (i >= 1 and i <= 9):
        s = "000" + str(i)
    elif (i >= 10 and i <= 99):
        s = "00" + str(i)
    elif (i >= 100 and i <= 999):
        s = "0" + str(i)
    else:
        s = str(i)
    browser.get('https://pesuacademy.com')
    sleep(2)
    browser.find_element(By.ID, "knowClsSection").click()
    inp = browser.find_element(By.ID, "knowClsSectionModalLoginId")
    inputPRN = st + yr + "0" + s
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

        f1.write(strRow + "\n")

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

f1.close()
print("File closed")
browser.close()
print("Browser closed")
database.close()
print("db closed")
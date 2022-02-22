from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass

def orario_setup():
    f = open('orario.csv','r')
    d = {}
    for line in f:
        l = line.strip().split(',')
        if l[0] not in d.keys():
            d[l[0]] = []
        d[l.pop(0)].append(l)
    f.close()
    return d

def print_intro():
    print("Welcome, supported courses are: ")
    d = orario_setup()
    for i in d.keys():
        print(i)
    print('\n')
    return d

def date_range(start, end):
    delta = end - start  # as timedelta
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return days

def polish_date(date):
    date = date.split(',')
    start_date = date[0].split('-')
    start_date = datetime(int(start_date[2]), int(start_date[1]), int(start_date[0]))
    end_date = date[1].split('-')
    end_date = datetime(int(end_date[2]), int(end_date[1]), int(end_date[0]))
    if start_date.weekday() != 0:
        print("Start date is not Monday. Quitting.")
        quit()
    if start_date <= datetime.now():
        print("Start date must be at least one day before today. Quitting.")
        quit()
    if end_date.weekday() != 4:
        print("End date is not Friday. Quitting.")
        quit()
    if end_date <= start_date:
        print("End date must be after start date. Quitting.")
        quit()
    days = date_range(start_date, end_date)
    if len(days) != 5:
        print("Not 7 days. Quitting.")
        quit()
    l = []
    for elem in days:
        l.append(elem.strftime("%d/%m/%y"))
    return l

def main():
    d = print_intro()
    corsi_scelti = input("Write courses separated by a comma, as written in the above message (eg. course1,course2,...): ").strip().split()
    settimana = input("Write the week of interest (monday to friday both included, eg. DD-MM-YYYY,DD-MM-YYYY): ").strip()
    settimana = polish_date(settimana)
    user_username = input("Write username: ").strip()
    user_password = getpass("Write password: ").strip()
    opts = Options()
    opts.headless = True
    print("Spawning Firefox web driver...")
    browser = Firefox(options=opts)
    print("Done.")
    print("Getting https://prodigit.uniroma1.it/...")
    browser.get("https://prodigit.uniroma1.it/")
    print("Done.")
    print("Accepting cookies...")
    WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="cookieChoiceDismiss"]'))).click()
    print("Done.")
    username = browser.find_element(By.NAME, "Username")
    password = browser.find_element(By.NAME, "Password")
    username.send_keys(user_username)
    password.send_keys(user_password)
    print("Authenticating...")
    browser.find_element(By.XPATH, "//input[@type='submit' and @value='Accedi']").click()
    browser.get("https://prodigit.uniroma1.it/prenotazioni")
    try:
        browser.find_element(By.NAME, "lingua")
    except:
        print("Login unsuccessful. Quitting.")
        quit()
    print("Done.")

    for corso in corsi_scelti:
        for entry in d[corso]:
            the_time = entry[0].strip().split('-')
            start_time, end_time = (the_time[0], the_time[1])

            browser.get("https://prodigit.uniroma1.it/prenotazioni")
            browser.find_element(By.NAME, "Prenota il posto in aula").click()
    
            select = Select(browser.find_element(By.ID, "codiceedificio"))
            select.select_by_visible_text(entry[2])
   
            select = Select(browser.find_element(By.NAME, "aula"))
            select.select_by_visible_text(entry[3])

            table = browser.find_elements(By.CLASS_NAME, "table-striped")[3]
            for row in table.find_elements(By.CSS_SELECTOR, 'tr'):
                cells = row.find_elements(By.TAG_NAME, 'td') 
                if cells[1].text in settimana:
                    select = Select(cells.find_elements(By.CSS_SELECTOR, 'select')[0])
                    select.select_by_visible_text(start_time)
                    select = Select(cells.find_elements(By.CSS_SELECTOR, 'select')[1])
                    select.select_by_visible_text(end_time)
            browser.find_element(By.NAME, 'dichiarazione').click()
            browser.find_element(By.ID, 'btnprenota').click()

    browser.quit()

if __name__ == "__main__":
    main()

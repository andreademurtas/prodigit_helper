from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass

lista_giorni = ["Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi"]

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
    print("__________                   .___.__       .__  __    .__           .__                       \n\\______   \\_______  ____   __| _/|__| ____ |__|/  |_  |  |__   ____ |  | ______   ___________ \n |     ___/\\_  __ \\/  _ \\ / __ | |  |/ ___\\|  \\   __\\ |  |  \\_/ __ \\|  | \\____ \\_/ __ \\_  __ \\\n |    |     |  | \\(  <_> ) /_/ | |  / /_/  >  ||  |   |   Y  \\  ___/|  |_|  |_> >  ___/|  | \\/\n |____|     |__|   \\____/\\____ | |__\\___  /|__||__|   |___|  /\\___  >____/   __/ \\___  >__|   \n                              \\/   /_____/                 \\/     \\/     |__|        \\/")
    print("")
    print("Tool per la prenotazione automatica delle aule su Prodigit.\nI corsi attualmente supportati sono:")
    d = orario_setup()
    for i in d.keys():
        print(i)
    print('')
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
        print("La data iniziale non è Lunedì. Uscendo...")
        quit()
    if start_date <= datetime.now():
        print("Non è possibile prenotare l'aula per oggi o per giorni precedenti. Uscendo...")
        quit()
    if end_date.weekday() != 4:
        print("La data finale non è Venerdì. Uscendo...")
        quit()
    if end_date <= start_date:
        print("La data finale deve successiva a quella iniziale. Uscendo...")
        quit()
    days = date_range(start_date, end_date)
    if len(days) != 5:
        print("Il periodo selezionato deve contenere 5 giorni. Uscendo...")
        quit()
    l = []
    for elem in days:
        l.append(elem.strftime("%d/%m/%Y"))
    return l

def main():
    d = print_intro()
    corsi_scelti = input("Scrivi i corsi come li leggi nel messaggio sopra, separati da una virgola (es. corso1,corso2,...): ").strip().split()
    for corso in corsi_scelti:
        if corso not in d.keys():
            print("Uno o più corsi non presenti nel database. Uscendo...")
            quit()
    settimana = input("Scrivi il giorno iniziale e quello finale della settimana di interesse, separati da una virgola (Da Lunedì a Venerdì inclusi, es. DD-MM-YYYY,DD-MM-YYYY): ").strip()
    settimana = polish_date(settimana)
    user_username = input("Username: ").strip()
    user_password = getpass("Password: ").strip()
    opts = Options()
    opts.headless = True
    print("Lanciando il web driver...")
    browser = Firefox(options=opts)
    print("Fatto.")
    print("Richiedendo https://prodigit.uniroma1.it/...")
    browser.get("https://prodigit.uniroma1.it/")
    print("Fatto.")
    print("Accettando i cookies...")
    WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="cookieChoiceDismiss"]'))).click()
    print("Done.")
    username = browser.find_element(By.NAME, "Username")
    password = browser.find_element(By.NAME, "Password")
    username.send_keys(user_username)
    password.send_keys(user_password)
    print("Facendo il login...")
    browser.find_element(By.XPATH, "//input[@type='submit' and @value='Accedi']").click()
    browser.get("https://prodigit.uniroma1.it/prenotazioni")
    try:
        browser.find_element(By.NAME, "lingua")
    except:
        print("Login non andato a buon fine. Uscendo...")
        quit()
    print("Fatto.")

    for corso in corsi_scelti:
        for entry in d[corso]:
            yes_or_no = input("Vuoi prenotare la lezione del corso {} di {}? Orario: {} [Y/N]: ".format(corso, entry[1], entry[0]))
            if yes_or_no != "Y":
                print("Saltando...")
                continue
            the_time = entry[0].strip().split('-')
            start_time, end_time = (the_time[0], the_time[1])

            browser.get("https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-aula-lezioni")

            select = Select(browser.find_element(By.ID, "codiceedificio"))
            select.select_by_visible_text(entry[2])
   
            select = Select(browser.find_element(By.NAME, "aula"))
            select.select_by_visible_text(entry[3])
            
            table = browser.find_elements(By.CLASS_NAME, "table-striped")[3]
            for row in table.find_elements(By.CSS_SELECTOR, 'tr'):
                cells = row.find_elements(By.TAG_NAME, 'td') 
                if cells[1].text in settimana and cells[0].text == entry[1]:
                    select = Select(cells[2].find_element(By.CSS_SELECTOR, 'select'))
                    select.select_by_visible_text(start_time)
                    break
            table = browser.find_elements(By.CLASS_NAME, "table-striped")[3]
            for row in table.find_elements(By.CSS_SELECTOR, 'tr'):
                cells = row.find_elements(By.TAG_NAME, 'td') 
                if cells[1].text in settimana and cells[0].text == entry[1]:
                    select = Select(cells[3].find_element(By.CSS_SELECTOR, 'select'))
                    select.select_by_visible_text(end_time)
                    break
            browser.find_element(By.NAME, 'dichiarazione').click()
            browser.find_element(By.ID, 'btnprenota').click()
            print("Fatto")
    browser.quit()
if __name__ == "__main__":
    main()

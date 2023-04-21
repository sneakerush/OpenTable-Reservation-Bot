from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from datetime import date
from pathlib import Path
from datetime import datetime
import time
import schedule
import json


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# / / / / / / / / / / / / / / / User inputs / / / / / / / / / / / / / / / /

link = input("\nEnter link: ")
scheduleTime = input("Enter start time:(Leave blank if monitoring or ATC)(00:00:00 Format) ")
monitor_delay = input("Enter monitor delay: ")
while monitor_delay == '':
    print('Error, must enter a value for monitor delay...')
    monitor_delay = input("Enter monitor delay: ")

# / / / / / / / / / / / / / Ensures Chromedriver is always updated / / / / / / / / / /

driver = webdriver.Chrome(ChromeDriverManager().install())

# / / / / / / / / / / / / / / / file path for cookies / / / / / / / / / / / / / / / 

file = Path("cookies.json")

# / / / / / / / / / / / / / / / to store and load cookies from browser / / / / / / / 

def save_cookie(driver, file):
    print(f'{datetime.now()} Please login to your OpenTable account. You have 60 seconds')
    driver.get('https://www.opentable.com')
    time.sleep(60)
    driver.refresh()
    with open(file, 'w') as filehandler:
        json.dump(driver.get_cookies(), filehandler)
    print(f'{datetime.now()} File created')
    driver.refresh()
    print(f'{datetime.now()} Beep Boop, Get ready')
    time.sleep(10)
    # driver.get('https://www.opentable.com')

#  / / / / / / / / / / / / / / / loads cookies into browser / / / / / / / / / / /

def load_cookies(driver, file):
    driver.get('https://www.opentable.com')
    # time.sleep(1)
    with open(file, 'r') as cookiesfile:
        cookies = json.load(cookiesfile)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    print(f'{datetime.now()} Loaded cookies')

    # goes to linked page for checkout
    driver.get(link)

#  / / / / / / / / / / / / / / / finds elements / / / / / / / / / / / / / / / 
    print(f'{datetime.now()} Starting now...')
    def find_elements():
        # to find thid XPATH for opentable, i looked up the tooltip under the /a tag href and clicked the second
        # subset of tooltips. 4 are found per timeslot. e.g: tooltip-1577638503
        # find a time
        st = time.time()
        findaTime = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/main/div/div[2]/div[2]/div/article/div/div[5]/button')))
        findaTime.click()
        if monitor_delay != '':
            if findaTime:
                print(f'{datetime.now()} Clicking finding a time...')
                print(f'{datetime.now()} Timeslots potentially unavailable...')
                print(f'{datetime.now()} Retrying in roughly {monitor_delay}s...')
        else:
            print(f'{datetime.now()} Clicking finding a time...')

        # finding an available time slot
        # # driver.find will invoke an error - NoSuchElementException which will trigget refresh faster and accurately
        # driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div[2]/div[2]/div/article/div/article/ul/li[2]/a').click()
        # however, if the timeslot is available, this should still invoke being that it is faster.
        timeslot = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mainContent"]/div/div[2]/div[2]/div/article/div/article/ul/li[2]/a')))
        if timeslot:
            timeslot.click()
            print(f'{datetime.now()} Finding a timeslot...')

        # select seating type
        seatingType = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[text()='Select']")))
        seatingType.click()
        if seatingType:
            print(f'{datetime.now()} Selecting seating type...')
        
        # confirm
        reservationConf = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'complete-reservation')))
        reservationConf.click()
        if reservationConf:
            print(f'{datetime.now()} Confirming reservation...')
            print(f'{datetime.now()} Successful bot, Good boy...')
        else:
            print(f'{datetime.now()} Hmm, an error...')

        et = time.time() - st
        print('Elapsed time:', time.strftime("%H:%M:%S", time.gmtime(et)))
        print('ctrl c to exit bot...')


#  / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / 

    # if a sleepDelay is entered then it goes this route
    if scheduleTime != "":
        print(f'Bot starting at {scheduleTime}...')
        # will wait at restraunt page until scheduleTime starts to execute find_elements
        while True:
            try:
                schedule.every().day.at(scheduleTime).do(find_elements)
            except TimeoutException:
                time.sleep(int(monitor_delay))
                driver.refresh()
            else:
                while True:
                    try:
                        schedule.run_pending()
                        time.sleep(1)
                    except TimeoutException:
                        time.sleep(int(monitor_delay))
                        driver.refresh()
                        


    elif monitor_delay:
        print(f'{datetime.now()} Monitor starting now...')
        while True:
            try:
                find_elements()
            # driver is waiting for timeout to then refresh, not time.sleeps fault
            except TimeoutException:
                time.sleep(int(monitor_delay))
                driver.refresh()

# # / / / / / / / / / / / / executing functions above / / / / / / / / / / / /

if file.exists():
    load_cookies(driver, file)
else:
    save_cookie(driver, file)
    load_cookies(driver, file)

#  / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / 
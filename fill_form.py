import os
import random
import time
import pandas as pd
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from aptos_sdk.account import Account

from config import MIN_SLEEP, MAX_SLEEP, GOOGLE_FORM_URL
from logger import setup_gay_logger

extension_subdir = "CapSolver.Browser.Extension-chrome-v1.10.3"
EXEL = "data.xlsx"
df = pd.read_excel(EXEL, engine='openpyxl')


def check_for_element_with_text(driver, logger):
    end_time = time.time() + 30
    expected_text = "Your response has been recorded"
    while time.time() < end_time:
        try:
            element = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[3]')
            if element.text == expected_text:
                logger.info("Expected text found on the page")
                return True
        except NoSuchElementException:
            pass
        time.sleep(1)
    logger.info("Expected text not found within timeout")
    return False

def fill_the_form(driver, address: str, mail: str, logger):
    driver.get(GOOGLE_FORM_URL)
    logger.info(f"Form opened")

    first_input_xpath = "/html/body/div[1]/div[2]/form/div[2]/div/div[2]/div[1]/div/div[1]/div[2]/div[1]/div/div[1]/input"
    second_input_xpath = "/html/body/div[1]/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input"
    button_xpath = "/html/body/div[1]/div[2]/form/div[2]/div/div[3]/div[3]/div[1]/div"

    first_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, first_input_xpath)))
    second_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, second_input_xpath)))
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))

    first_input.send_keys(mail)
    second_input.send_keys(address)
    button.click()
    logger.info(f"Form submitted for {mail}")

    return check_for_element_with_text(driver, logger)


script_dir = os.path.dirname(os.path.realpath(__file__))
extension_dir = os.path.join(script_dir, extension_subdir)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument(f'--load-extension={extension_dir}')

driver = webdriver.Chrome(options=chrome_options)
driver.get(GOOGLE_FORM_URL)

for index, row in df.iterrows():
    if row['Done?'] == 1:
        aptos_key = row['Aptos Key']
        mail = row['Mail']
        account = Account.load_key(aptos_key)
        address = account.address()
        logger = setup_gay_logger(str(address))

        try:
            result = fill_the_form(driver, str(address), mail, logger)
            if result:
                df.at[index, 'Done?'] = 2
                df.to_excel(EXEL, index=False)
                logger.info(f"Form successfully processed for {mail}")
                time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))
            else:
                logger.warning(f"Form submission failed for {mail}")
                continue
        except Exception as e:
            try:
                driver.close()
            except Exception:
                pass
            driver = webdriver.Chrome(options=chrome_options)
            logger.error(f"Error processing row {index}: {e}")
            continue


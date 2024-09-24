""" ОСНОВНОЙ КОД ПРОГРАММЫ ПО ПАРСИНГУ СПИСКА ТУРНИРОВ """

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
from dotenv import load_dotenv

URL = 'https://www.sport-liga.pro/ru/table-tennis/tournaments'

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# загрузка нужных переменных с телефоном и паролем
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    USER_PHONE = os.getenv("USER_PHONE")
    USER_PASSWORD = os.getenv("USER_PASSWORD")


# авторизация и загрузка страницы
def authorisation(url):
    print('Идет загрузка данных')
    driver = webdriver.Chrome()  # Используйте драйвер для вашего браузера

    driver.get(url)
    driver.maximize_window()

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//header/div[2]/p')))
    login_button.click()

    # Переключаемся на вкладку "Телефон"
    phone_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//form/div[1]/div[2]')))
    phone_tab.click()

    # Заполняем поле "Номер телефона"
    phone_field = driver.find_element(By.XPATH, '//form/div[2]/label/input')
    phone_field.send_keys(USER_PHONE)

    # Заполняем поле "Пароль"
    password_field = driver.find_element(By.XPATH, '//form/div[3]/label/input')
    password_field.send_keys(USER_PASSWORD)

    # Нажимаем кнопку "Войти"
    login_button = driver.find_element(By.XPATH, '//form/button[2]')
    login_button.click()

    # ожидаем загрузки страницы
    time.sleep(3)
    print('Страница загружена')
    return driver


# получение списка всех турниров
def get_more_results(driver):
    more_results = driver.find_element(By.XPATH, '//div[1]/button[2]/div')
    while True:
        try:
            more_results.click()
            time.sleep(0.5)
            driver.execute_script('window.scrollBy(0,1000)')
            time.sleep(0.5)
            more_results = driver.find_element(By.XPATH,
                                               '//div[1]/button[2]/div')
            time.sleep(0.5)
        except Exception as ex:
            # print(ex)
            break


# получение ссылок на турниры
def get_tournament_url_list(driver):
    results = driver.find_elements(By.XPATH, '//table/tbody/tr/td[2]/a')
    lst_url = [res.get_attribute("href") for res in results]
    return lst_url


# получение списка участников турниров
def get_list_of_players(driver):
    button = driver.find_elements(By.XPATH, '//table/tbody/tr/td[4]')

    lst_players = []
    for i, but in enumerate(button):
        but.click()
        time.sleep(1.25)
        family = driver.find_elements(
            By.XPATH,
            f'//table/tbody/tr[{i + 1}]/td[4]//table/tbody/tr/td[2]/a/div/p')

        lst_players.append([el.text for el in family])
    driver.find_element(By.XPATH, f'//table/tbody/tr[{i + 1}]/td[4]').click()
    time.sleep(0.5)
    return lst_players


def start_parser_tournament(url, dat):
    dri = authorisation(url + f'?date_from={dat}')
    get_more_results(dri)
    lst_url = get_tournament_url_list(dri)
    lst_players = get_list_of_players(dri)

    data_res = pd.DataFrame()
    tours = dri.find_elements(By.XPATH, '//table/tbody/tr/td[2]/a')
    date = dri.find_elements(By.XPATH, '//table/tbody/tr/td[1]/a')
    status = dri.find_elements(By.XPATH, '//table/tbody/tr/td[5]')

    data_res['date'] = [el.get_attribute("text").split('.')[0] for el in date]
    data_res['time'] = [el.get_attribute("text").split(' ')[-1] for el in date]
    data_res['tables'] = [el.get_attribute("text").split('.')[0].split(' ')[1]
                          for el in tours]
    data_res['liga'] = [el.get_attribute("text").split('.')[1] for el in tours]
    data_res['players'] = lst_players
    data_res['url'] = lst_url
    data_res['status'] = [el.text for el in status]

    print('Данные о турнирах загружены')

    data_res.to_csv(f'./tours/tours_in_{dat}.csv', index=False)
    print('Данные о турнирах записаны')


if __name__ == '__main__':
    URL = 'https://www.sport-liga.pro/ru/table-tennis/tournaments'
    date_now = '2024-09-24'
    start_parser_tournament(URL, date_now)

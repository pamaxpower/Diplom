####  Загрузка истории без последних 5 матчей

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
from dotenv import load_dotenv
from parser_tournaments import authorisation

# загрузка нужных переменных с телефоном и паролем
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    USER_PHONE = os.getenv("USER_PHONE")
    USER_PASSWORD = os.getenv("USER_PASSWORD")


# получение url сиска игр
def get_match_list_url(driver):
    match_list = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//div[2]/div[3]/div/div/div/div[1]/a')))
    match_list = match_list[:len(match_list) // 2]
    print(match_list)
    return match_list


# получение информации о матчах
def get_match_infomation(lgu, dri):
    # информация о личных встречах
    game = []

    for i, row in enumerate(lgu):
        match_url = row.get_attribute("href")

        dri.execute_script("window.open('');")
        dri.switch_to.window(dri.window_handles[-1])
        dri.get(match_url)

        try:
            history_link = WebDriverWait(dri, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                '//table/tr[5]/td[2]/span/a')))
            history_link.click()

            res = WebDriverWait(dri, 3).until(
                EC.presence_of_element_located((By.XPATH, '//section/div[2]'))
            ).find_element(By.XPATH, '//section/div[2]').text
            game.append(res)

        except Exception as ex:
            print(ex)
            fio1 = dri.find_element(By.XPATH, '//section/a/span').text
            fio2 = dri.find_element(By.XPATH, '//section/ul/li[4]/a').text
            res = fio1 + ' 0 : 0 (0:0) ' + fio2
            game.append(res)

        dri.close()
        dri.switch_to.window(dri.window_handles[0])

    print(game)
    return game


# # обработка информации по матчам
def processing_match_information(game):
    player_1 = []
    player_2 = []
    games = []
    sets = []

    df = pd.DataFrame()

    for el in game:
        print(game)
        pl_1 = el.split(' ')[:3][0] + ' ' + el.split(' ')[:3][1][:1] + '.' + \
               el.split(' ')[:3][2][:1] + '.'
        player_1.append(pl_1)
        pl_2 = el.split(' ')[-3:][0] + ' ' + el.split(' ')[-3:][1][:1] + '.' + \
               el.split(' ')[-3:][2][:1] + '.'
        player_2.append(pl_2)
        games.append(''.join(el.split(' ')[3:6]))
        sets.append(el.split(' ')[6])

    df['player_1'] = player_1
    df['player_2'] = player_2
    df['games'] = games
    df['sets'] = sets

    return df


# объединение всех функций


def my_func(url):
    # проходим авторизацию на сайте
    driver = authorisation(url)
    # получаем элементы с ссылками на игры турнира
    h2h_games = get_match_list_url(driver)
    # получаем историю личных встреч
    # games_info = get_match_infomation(h2h_games, driver)
    # # преобразуем данные в датафрейм
    # df = processing_match_information(games_info)

    return h2h_games
    # return df


if __name__ == "__main__":
    URL = 'https://www.sport-liga.pro/ru/table-tennis/tournaments/45714'

    # t0 = time.time()
    data1 = my_func(URL)
    # t1 = time.time()
    # print(t1 - t0)

    print(data1)

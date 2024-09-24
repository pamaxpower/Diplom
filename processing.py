import pandas as pd


def processing_players(df):
    # ОБРАБОТКА СТОЛБЦА С УЧАСТНИКАМИ
    players = []

    for i in range(len(df['players'])):
        full_name = []
        for j in range(len(df['players'][i].split(','))):
            full_name.append(df['players'][i].split(',')[j].strip(r"[/ ']"))
        players.append(full_name)

    players = [[fio.split(' ')[0] + ' ' + fio.split(' ')[1][0] + '.'
                + fio.split(' ')[2][0] + '.' for fio in player] for player in
               players]

    df['players'] = players
    return df


# ПОИСК ИГРОКА ПО ФАМИЛИИ

# вводим фамилию игрока
# name = input('Введите фамилию игрока: ')


def search_player(name, df):
    tours = pd.DataFrame()

    for i in range(len(df['players'])):
        for full_name in df['players'][i]:
            if name.lower() == full_name.split(' ')[0].lower():
                tours = tours._append(df.iloc[i], ignore_index=True)
    return tours


def check_date(date_str):
    # Разделяем строку на год, месяц и день
    year, month, day = map(int, date_str.split('-'))
    # устанавливаем флаг корректности даты 
    flag = True
    # Проверяем корректность года, месяца и дня
    if not (1 <= month <= 12):
        flag = False
    if not (1 <= day <= 31):
        flag = False
    # Проверяем корректность дня для месяцев с 30 днями
    if month in [4, 6, 9, 11] and day == 31:
        flag = False
    # Проверяем корректность дня для февраля
    if month == 2:
        if (year % 4 == 0 and (
                year % 100 != 0 or year % 400 == 0)) and day > 29:
            flag = False
        elif day > 28:
            flag = False
    return flag


if __name__ == "__main__":
    dat = '2024-09-18'
    data = pd.read_csv(f'./tours/tours_in_{dat}.csv')

    data = processing_players(data)

    print(data['players'])

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from db.operations import get_all_workers

week_days = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]


day_time = [
    ["08:00", "09:00", "10:00"],
    ["11:00", "12:00", "13:00"],
    ["14:00", "15:00", "16:00"],
    ["17:00", "18:00", "19:00"],
    ["20:00", "21:00", "22:00"],
    ["23:00", "00:00", "01:00"],
    ["02:00", "03:00", "04:00"],
    ["05:00", "06:00", "07:00"],
]



def day_time_board():
    k = InlineKeyboardMarkup()

    for g in day_time:
        row = []

        for t in g:
            b = InlineKeyboardButton(t, callback_data=t)
            row.append(b)

        k.row(*row)
    return k


def workers_board():
    workers = get_all_workers()

    k = InlineKeyboardMarkup()

    for worker in workers:
        b = InlineKeyboardButton(worker.username, callback_data=worker.id)
        k.add(b)

    return k


def choose_week_day_table():

    keyboard = InlineKeyboardMarkup()

    for i in range(len(week_days)):
        b = InlineKeyboardButton(week_days[i], callback_data=f"{i}")
        keyboard.add(b)

    return keyboard


def main_menu():
    k = ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(KeyboardButton('Добавить работника'))
    k.row(KeyboardButton('Список одноразовых задач'), KeyboardButton('Список периодичных задач'))
    k.row(KeyboardButton('Добавить одноразовую задачу'), KeyboardButton('Добавить периодичную задачу'))

    return k
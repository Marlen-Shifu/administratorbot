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
    ["09:00", "09:30", "10:00", "10:30"],
    ["11:00", "11:30", "12:00", "12:30"],
    ["13:00", "13:30", "14:00", "14:30"],
    ["15:00", "15:30", "16:00", "16:30"],
    ["17:00", "17:30", "18:00", "18:30"],
    ["19:00", "19:30", "20:00", "20:30"],
    ["21:00", "21:30", "22:00", "22:30"],
    ["23:00", "23:30", "00:00", "00:30"],
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

    k.add(KeyboardButton('Список работников'), KeyboardButton('Добавить работника'))
    k.row(KeyboardButton('Список одноразовых задач'), KeyboardButton('Добавить одноразовую задачу'))
    k.row(KeyboardButton('Список периодичных задач'), KeyboardButton('Добавить периодичную задачу'))
    k.row(KeyboardButton('Отчет'))

    return k


def worker_menu():
    k = ReplyKeyboardMarkup(resize_keyboard=True)

    k.row(KeyboardButton('Мой список работников'), KeyboardButton('Мои периодичные задачи'))
    k.row(KeyboardButton('Мои одноразовые задачи'), KeyboardButton('Добавить одноразовую задачу'))

    return k

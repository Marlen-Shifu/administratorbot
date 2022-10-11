from aiogram import types

from boards import week_days
from db.operations import *


async def worker_onetime_tasks(mes: types.Message):
    user = get_user_by_userid(mes.from_user.id)

    user_tasks = get_onetime_tasks_of_user(user.id)

    k = types.InlineKeyboardMarkup()

    for user_task in user_tasks:
        k.add(types.InlineKeyboardButton(f"{user_task.title}", callback_data=f"worker_o_task_inf {user_task.id}"))

    await mes.answer("Ваши одноразовые задания", reply_markup=k)


async def worker_o_task_info(callback: types.CallbackQuery):
    data = callback.data.split(' ')
    await callback.answer('')

    task_id = data[1]
    task = get_task(task_id)

    await callback.bot.send_message(callback.from_user.id,
f"""
Название: {task.title}
Описание: {task.description}
Время: {task.time}"""
)



async def worker_periodic_tasks(mes: types.Message):
    user = get_user_by_userid(mes.from_user.id)

    user_tasks = get_periodic_tasks_of_user(user.id)

    await mes.bot.send_message(840647074, f"{user_tasks}")

    k = types.InlineKeyboardMarkup()

    for user_task in user_tasks:
        k.add(types.InlineKeyboardButton(f"{user_task.title}", callback_data=f"worker_p_task_inf {user_task.id}"))

    await mes.answer("Ваши периодичные задания", reply_markup=k)



async def worker_p_task_info(callback: types.CallbackQuery):
    data = callback.data.split(' ')
    await callback.answer('')

    task_id = data[1]
    task = get_periodic_task(task_id)

    days_list = ""
    counter = 1

    for day in task.get_days_list():
        days_list += f"\n             {counter}. {week_days[int(day) - 1]}"
        counter += 1

    times_list = ""
    counter = 1

    for time in task.get_times_list():
        times_list += f"\n             {counter}. {time}:00"
        counter += 1

    await callback.bot.send_message(callback.from_user.id,
                                          f"""
Название: {task.title}
Описание: {task.description}
Дни: {days_list}
Времена: {times_list}""")

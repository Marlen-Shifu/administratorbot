
from aiogram import types
from aiogram.dispatcher import FSMContext

from boards import main_menu
from db.operations import *

from states import DeleteWorker


async def workers_list(mes: types.Message):
    workers_list = get_all_workers()

    if workers_list == None:
        await mes.answer("Список пуст")

        return

    k = types.InlineKeyboardMarkup()

    for worker in workers_list:

        k.add(types.InlineKeyboardButton(f'Удалить {worker.username}', callback_data=f'delete_worker {worker.id}'))

    await mes.answer("Список работников", reply_markup=k)


async def my_workers_list(mes: types.Message):
    workers_list = get_all_workers()

    if workers_list == None:
        await mes.answer("Список пуст")

        return

    k = types.InlineKeyboardMarkup()

    for worker in workers_list:

        k.add(types.InlineKeyboardButton(f'{worker.username}', callback_data=f'1'))

    await mes.answer("Список работников", reply_markup=k)


async def delete_worker_confirm(callback: types.CallbackQuery):
    data = callback.data.split(' ')
    await callback.answer()

    worker_id = data[1]
    worker = get_user(worker_id)

    k = types.InlineKeyboardMarkup()

    k.add(types.InlineKeyboardButton('Да', callback_data=f'delete_worker_ans yes {worker_id}'), types.InlineKeyboardButton('Нет', callback_data=f'delete_worker_ans no'))

    await DeleteWorker.confirm.set()

    await callback.bot.send_message(callback.from_user.id, f"Вы уверены что хотите удалить работника {worker.username}", reply_markup=k)


async def delete_worker_answer(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split(' ')
    await callback.answer()

    answer = data[1]

    if answer == 'yes':
        try:
            worker_id = data[2]
            delete_worker(worker_id)

            await callback.bot.send_message(callback.from_user.id, f"Работник успешно удален")

        except Exception as e:

            await callback.bot.send_message(callback.from_user.id, f"Какая то ошибка (")
            raise e

        await state.finish()

    elif answer == 'no':
        await callback.bot.send_message(callback.from_user.id, f"Отмена", reply_markup=main_menu())

        await state.finish()
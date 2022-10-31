
from celery_bot import ask_task

from datetime import datetime

from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData

from aiogram_calendar import SimpleCalendar

# from utils import mail

from db.operations import *
from states import *
from boards import *

from config import PASSWORD, POSITIONS
from utils.mailing.mail import mail



async def cancel_btn(mes: types.Message, state: FSMContext):

    await state.finish()

    await mes.answer('Отмена выполнения', reply_markup=main_menu())


async def user_start(mes: types.Message):
    user = get_user(None, username=mes.from_user.username)

    if user == None:
        await mes.answer("Здравствуйте, это Администратор Бот. \nВас нет в нашей базе(\nЕсли вы работник обратитесь к вашему менеджеру, а если вы представитель бизнеса обратитесь к @Marlen45")

    elif user != None and user.user_id == None:
        update_user_id(user, mes.from_user.id)
        user = get_user_by_userid(mes.from_user.id)

    if user.position == POSITIONS.ADMIN:
        await mes.answer(f"Здравствуйте {user.username}!", reply_markup=main_menu())
    else:
        await mes.answer(f"Здравствуйте {user.username}!", reply_markup=worker_menu())


async def add_admin(mes: types.Message):

    await RequirePasswordState.password.set()

    await mes.answer("Введите пароль")


async def ask_password(mes: types.Message):

    if mes.text == PASSWORD:
        await RegisterAdminState.username.set()
        await mes.answer("Отправьте username")


async def ask_admin_username(mes: types.Message, state: FSMContext):

    result = add_user(username = mes.text, position = POSITIONS.ADMIN)

    if result == 'ok':
        await mes.answer("Админ успешно добавлен!")
    else:
        await mes.answer("Упс.. Какая то ошибка(")

    await state.finish()


async def add_worker(mes: types.Message):

    await RegisterWorkerState.username.set()

    await mes.answer("Отправьте username")


async def ask_user_username(mes: types.Message, state: FSMContext):

    result = add_user(username = mes.text, position = POSITIONS.WORKER)

    if result == 'ok':
        await mes.answer("Работник успешно добавлен!")
    else:
        await mes.answer("Упс.. Какая то ошибка(")

    await state.finish()


async def add_task(mes: types.Message):

    await AddOneTimeTask.title.set()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(KeyboardButton("Отмена"))

    await mes.answer("Введите название задания", reply_markup=k)


async def add_task_title(mes: types.Message, state: FSMContext):

    await state.update_data(title = mes.text)

    await AddOneTimeTask.description.set()

    k = ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(KeyboardButton('Пусто'))
    k.add(KeyboardButton('Отмена'))

    await mes.answer("Напишите описание задания задания", reply_markup=k)


async def add_task_des(mes: types.Message, state: FSMContext):

    await state.update_data(description = mes.text)

    await AddOneTimeTask.day.set()

    await mes.answer("Выберите день", reply_markup= await SimpleCalendar().start_calendar())


async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    new_date = date.strftime("%Y-%m-%d")

    if selected:

        if datetime.datetime.today().day > date.day:
            await callback_query.message.answer("Выберите будущее время)", reply_markup=await SimpleCalendar().start_calendar())

        else:
            await state.update_data(day = new_date)

            await AddOneTimeTask.time.set()

            await callback_query.bot.send_message(callback_query.from_user.id, "Выберите время", reply_markup = day_time_board())


async def add_task_time(callback_query: CallbackQuery, state:FSMContext):

    time = callback_query.data

    for g in day_time:
        if time in g:

            await state.update_data(time = time)

            await callback_query.message.edit_reply_markup(reply_markup=None)

            await AddOneTimeTask.workers.set()

            await callback_query.bot.send_message(callback_query.from_user.id, "Назначте сотрудников", reply_markup = workers_board())

            return

    await callback_query.bot.send_message(callback_query.from_user.id, "Какая то ошибка(")


async def add_task_workers(callback_query: CallbackQuery, state:FSMContext):

    data = callback_query.data
    await callback_query.answer('')

    if data != "finish":

        worker = get_user(data)

        task_data = await state.get_data()

        workers = task_data.get('workers')

        k = InlineKeyboardMarkup()
        k.add(InlineKeyboardButton("Продолжить", callback_data='finish'))


        if workers != None:
            workers.append(data)
            new_workers_list = workers
        else:
            new_workers_list = [data]


        await state.update_data(workers = new_workers_list)
        await callback_query.bot.send_message(callback_query.from_user.id, f"Был добавлен сотрудник @{worker.username}")


        worker_list = ""
        counter = 1

        for worker_id in new_workers_list:
            worker = get_user(worker_id)
            worker_list += f"\n{counter}. {worker.username}"
            counter += 1

        await callback_query.bot.send_message(callback_query.from_user.id, f"Выбранные сотрудники: {worker_list}", reply_markup=k)

    else:
        data = await state.get_data()

        k = ReplyKeyboardMarkup(resize_keyboard=True)
        k.add(KeyboardButton("Да"), KeyboardButton("Нет"))

        worker_list = ""
        counter = 1

        for worker_id in data.get('workers'):
            worker = get_user(worker_id)
            worker_list += f"\n         {counter}. {worker.username}"
            counter += 1


        await callback_query.bot.send_message(callback_query.from_user.id,
f"""Вы подтверждаете создание задания?
        Название: {data.get('title')}
        Описание: {data.get('description')}
        День: {data.get('day')}
        Время: {data.get('time')}
        Назначенные работники: {worker_list}""",
reply_markup=k)

        await AddOneTimeTask.confirm.set()


async def add_task_confirm(mes: types.Message, state: FSMContext):

    if mes.text == "Да":

        data = await state.get_data()

        workers_list = data.get('workers')

        task_id = create_task(
            title=data.get('title'),
            description=data.get('description'),
            date = data.get('day'),
            time = data.get('time'),
            creator_id=get_user(id = None, username=mes.from_user.username).id,
            workers_list=workers_list,
        )

        for worker_id in data.get('workers'):
            worker = get_user(worker_id)

            mail(worker.user_id, f"Вам назначили задание:\n{data.get('title')}")

        offset = datetime.timedelta(hours=6)
        timez = datetime.timezone(offset)
        date_time = datetime.datetime.strptime(data.get('day') + ", " + data.get('time'), "%Y-%m-%d, %H:%M")

        date_time = date_time - offset

        run_time = datetime.datetime.now() + datetime.timedelta(seconds=3)

        c_task_id = ask_task.apply_async((task_id, mes.from_user.id), eta=run_time)

        update_celery_task_id(task_id, c_task_id)

        await state.finish()

        await mes.answer("Задача успешно создана", reply_markup=main_menu())

    elif mes.text == "Нет":
        await mes.answer("Сброс создания", reply_markup=main_menu())

        await state.finish()

    else:
        await mes.answer("Выберите Да или Нет")



async def answer_to_task(callback: types.CallbackQuery):
    data = callback.data.split(' ')
    await callback.answer()

    answer = data[1]

    task_id = data[2]
    task = get_task(task_id)

    answers = task.get_answers()

    user = get_worker_by_userid(callback.from_user.id)

    if task.is_user_answered(user.id):
        await callback.bot.send_message(callback.from_user.id, f'Вы уже ответили на данное задание')

    else:

        await TaskAnswer.comment.set()

        state = Dispatcher.get_current().current_state()

        await state.update_data(task_id = task_id)
        await state.update_data(answer = answer)

        k = ReplyKeyboardMarkup()
        k.add(KeyboardButton('Пусто'))
        k.add(KeyboardButton('Отмена'))

        await callback.bot.send_message(callback.from_user.id, f'Оставьте комментарий', reply_markup=k)


        # if answers is None:
        #     answers = [{"user_id": user.id, "answer": f"{answer}"}]
        # else:
        #     answers.append({"user_id": user.id, "answer": f"{answer}"})
        #
        # update_onetime_task_answers(task_id, answers)
        #
        # k = InlineKeyboardMarkup()
        #
        # k.add(InlineKeyboardButton('Оставить комментарий', callback_data=f'comment_task {task_id}'))
        #
        # await callback.bot.send_message(callback.from_user.id, f'Ответ записан. Спасибо)', reply_markup=k)


async def comment_task(mes: types.Message, state: FSMContext):

    data = await state.get_data()

    task_id = data.get('task_id')
    task = get_task(task_id)

    answer = data.get('answer')

    answers = task.get_answers()

    user = get_worker_by_userid(mes.from_user.id)

    if mes.content_type == 'text':
        value = mes.text
    elif mes.content_type == 'photo':
        value = mes.photo[-1].file_id

    if answers is None:
        answers = [{"user_id": user.id, "answer": f"{answer}", "type": mes.content_type, "value": value}]
    else:
        answers.append({"user_id": user.id, "answer": f"{answer}", "type": mes.content_type, "value": value})

    update_onetime_task_answers(task_id, answers)

    await mes.answer('Ответ записан. Спасибо)')

    await state.finish()
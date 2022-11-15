import datetime

from aiogram import types, Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData

from boards import workers_board, day_time_board, day_time, main_menu
from db.operations import get_user, get_user_by_userid, create_periodic_task, get_all_workers, get_periodic_task, \
    update_task_answers, get_worker_by_userid, get_periodic_task_answers, create_periodic_task_answer
from states import AddPeriodicTask, PeriodicTaskAnswer
from utils.mailing.mail import mail

from boards import choose_week_day_table, week_days

from celery_bot import ask_periodic_task


async def add_task(mes: types.Message):
    await AddPeriodicTask.title.set()
    
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(KeyboardButton("Отмена"))

    await mes.answer("Введите название задания", reply_markup=k)


async def add_task_title(mes: types.Message, state: FSMContext):
    await state.update_data(title=mes.text)

    await AddPeriodicTask.description.set()

    k = ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(KeyboardButton('Пусто'))
    k.add(KeyboardButton('Отмена'))

    await mes.answer("Напишите описание задания задания", reply_markup=k)


async def add_task_des(mes: types.Message, state: FSMContext):
    await state.update_data(description=mes.text)

    await AddPeriodicTask.choose_schedule_type.set()

    k = ReplyKeyboardMarkup()

    k.add(KeyboardButton('Выбрать дни недели'))
    k.add(KeyboardButton('Указать дни через дни'))

    await mes.answer("Выберите тип графика", reply_markup=k)


async def choose_schedule_type(mes: types.Message, state: FSMContext):
    if mes.text == "Выбрать дни недели":

        await state.update_data(schedule_type = 'week_days')

        await AddPeriodicTask.days.set()

        k = choose_week_day_table()

        k.add(InlineKeyboardButton('Рабочие дни', callback_data='work_days'))
        k.add(InlineKeyboardButton('Выходные дни', callback_data='rest_days'))
        k.add(InlineKeyboardButton('Все дни', callback_data='all_days'))

        await mes.answer("Выберите дни работы", reply_markup=k)

    elif mes.text == "Указать дни через дни":

        await state.update_data(schedule_type = 'work_rest')

        await AddPeriodicTask.work_days_count.set()

        k = ReplyKeyboardMarkup(resize_keyboard=True)

        k.add(KeyboardButton('Пусто'))
        k.add(KeyboardButton('Отмена'))

        await mes.answer("Отправьте количество рабочих дней", reply_markup=k)


async def get_work_days_count(mes: types.Message, state: FSMContext):

    try:
        work_days = int(mes.text)

    except Exception as e:
        await mes.answer('Введите число')
        return

    await state.update_data(work_days = work_days)
    await AddPeriodicTask.rest_days_count.set()

    await mes.answer("Отправьте количество выходных дней")


async def get_rest_days_count(mes: types.Message, state:FSMContext):

    try:
        rest_days = int(mes.text)

    except Exception as e:
        await mes.answer('Введите число')
        return

    await state.update_data(rest_days = rest_days)

    await AddPeriodicTask.times.set()

    await mes.answer("Выберите времена", reply_markup=day_time_board())


async def process_simple_calendar(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    await callback_query.answer()

    if data != "finish":

        state_data = await state.get_data()
        choosen_days = state_data.get('days')

        k = InlineKeyboardMarkup()
        k.add(InlineKeyboardButton("Продолжить", callback_data='finish'))

        if data == 'work_days':
            new_days_list = [0, 1, 2, 3, 4]
            await callback_query.bot.send_message(callback_query.from_user.id, f"Вы выбрали Рабочие дни")

        elif data == 'rest_days':
            new_days_list = [5, 6]
            await callback_query.bot.send_message(callback_query.from_user.id, f"Вы выбрали Выходные дни")

        elif data == 'all_days':
            new_days_list = [0, 1, 2, 3, 4, 5, 6]
            await callback_query.bot.send_message(callback_query.from_user.id, f"Вы выбрали Все дни")

        else:

            if choosen_days is not None:
                choosen_days.append(data)
                new_days_list = choosen_days
            else:
                new_days_list = [data]

            await callback_query.bot.send_message(callback_query.from_user.id, f"Вы выбрали {week_days[int(data)]}")

        await state.update_data(days=new_days_list)

        days_list = ""
        counter = 1

        for day in new_days_list:
            days_list += f"\n{counter}. {week_days[int(day)]}"
            counter += 1

        await callback_query.bot.send_message(callback_query.from_user.id, f"Выбранные дни: {days_list}",
                                              reply_markup=k)

    else:

        await AddPeriodicTask.times.set()

        await callback_query.bot.send_message(callback_query.from_user.id, "Выберите времена",
                                              reply_markup=day_time_board())


async def add_task_time(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    await callback_query.answer()

    if data != "finish":

        for g in day_time:
            if data in g:

                k = InlineKeyboardMarkup()
                k.add(InlineKeyboardButton("Продолжить", callback_data='finish'))

                state_data = await state.get_data()

                choosen_times = state_data.get('times')

                if choosen_times is not None:
                    choosen_times.append(data)
                    new_times_list = choosen_times
                else:
                    new_times_list = [data]

                await state.update_data(times=new_times_list)
                await callback_query.bot.send_message(callback_query.from_user.id, f"Вы выбрали {data}")

                times_list = ""
                counter = 1

                for time in new_times_list:
                    times_list += f"\n{counter}. {time}"
                    counter += 1

                await callback_query.bot.send_message(callback_query.from_user.id, f"Выбранные времена: {times_list}",
                                                      reply_markup=k)

                return

    else:

        await AddPeriodicTask.workers.set()

        k = workers_board()

        k.add(InlineKeyboardButton('Все работники', callback_data='all_workers'))

        await callback_query.bot.send_message(callback_query.from_user.id, "Назначте сотрудников",
                                              reply_markup=k)

        return

    await callback_query.bot.send_message(callback_query.from_user.id, "Какая то ошибка(")


async def add_task_workers(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    await callback_query.answer('')

    if data != "finish":

        task_data = await state.get_data()

        workers = task_data.get('workers')

        k = InlineKeyboardMarkup()
        k.add(InlineKeyboardButton("Продолжить", callback_data='finish'))

        if data == 'all_workers':
            new_workers_list = []

            workers = get_all_workers()

            for worker in workers:
                new_workers_list.append(worker.id)

            await callback_query.bot.send_message(callback_query.from_user.id, f"Были добавлены все сотрудники")

        else:
            if workers is not None:
                workers.append(data)
                new_workers_list = workers
            else:
                new_workers_list = [data]

            worker = get_user(id=data)

            await callback_query.bot.send_message(callback_query.from_user.id,
                                                  f"Был добавлен сотрудник @{worker.username}")

        await state.update_data(workers=new_workers_list)

        worker_list = ""
        counter = 1

        for worker_id in new_workers_list:
            worker = get_user(worker_id)
            worker_list += f"\n{counter}. {worker.username}"
            counter += 1

        await callback_query.bot.send_message(callback_query.from_user.id, f"Выбранные сотрудники: {worker_list}",
                                              reply_markup=k)

    else:
        data = await state.get_data()

        k = ReplyKeyboardMarkup(resize_keyboard=True)
        k.add(KeyboardButton("Да"), KeyboardButton("Нет"))

        worker_list = ""
        counter = 1

        for worker_id in data.get('workers'):
            worker = get_user(worker_id)
            worker_list += f"\n             {counter}. {worker.username}"
            counter += 1

        if data.get('schedule_type') == 'week_days':

            days_list = ""
            counter = 1

            for day in data.get('days'):
                days_list += f"\n             {counter}. {week_days[int(day)]}"
                counter += 1

        elif data.get('schedule_type') == 'work_rest':
            days_list = f"{data.get('work_days')} на {data.get('rest_days')}"

        times_list = ""
        counter = 1

        for time in data.get('times'):
            times_list += f"\n             {counter}. {time}"
            counter += 1

        await callback_query.bot.send_message(callback_query.from_user.id,
                                              f"""Вы подтверждаете создание задания?
        Название: {data.get('title')}
        Описание: {data.get('description')}
        Дни: {days_list}
        Времена: {times_list}
        Назначенные работники: {worker_list}""",
                                              reply_markup=k)

        await AddPeriodicTask.confirm.set()


async def add_task_confirm(mes: types.Message, state: FSMContext):
    if mes.text == "Да":

        data = await state.get_data()

        workers_list = data.get('workers')

        if data.get('schedule_type') == 'week_days':

            task_id = create_periodic_task(
                title=data.get('title'),
                description=data.get('description'),
                days=data.get('days'),
                times=data.get('times'),
                creator_id=get_user(id=None, username=mes.from_user.username).id,
                workers_list=workers_list,
            )

        elif data.get('schedule_type') == 'work_rest':

            task_id = create_periodic_task(
                title=data.get('title'),
                description=data.get('description'),
                work_days_count = data.get('work_days'),
                rest_days_count = data.get('rest_days'),
                current_state=f"work:{data.get('work_days')}",
                times=data.get('times'),
                creator_id=get_user(id=None, username=mes.from_user.username).id,
                workers_list=workers_list,
            )

        for worker_id in data.get('workers'):
            worker = get_user(worker_id)

            mail(worker.user_id, f"Вам назначили задание:\n{data.get('title')}")

            # run_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
            #
            # ask_periodic_task.apply_async((task_id, mes.from_user.id), eta=run_time)

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
    task = get_periodic_task(task_id)

    answers = get_periodic_task_answers(task_id)

    user = get_worker_by_userid(callback.from_user.id)

    today = datetime.datetime.today()


    if today.minute > 30:
        minute = 30
    else:
        minute = 0

    def user_is_answered(user, answers_list):
        for answer in answers_list:
            if user.id == answer.user_id:
                await callback.bot.send_message(callback.from_user.id, f'{answer.time}')
                if answer.time.day == today.day and answer.time.hour == today.hour and answer.time.minute == minute:
                    return True

        return False

    if user_is_answered(user, answers):
        await callback.bot.send_message(callback.from_user.id, f'Вы уже ответили на данное задание')

    else:

        await PeriodicTaskAnswer.comment.set()

        state = Dispatcher.get_current().current_state()

        await state.update_data(task_id=task_id)
        await state.update_data(answer=answer)

        k = ReplyKeyboardMarkup()
        k.add(KeyboardButton('Пусто'))
        k.add(KeyboardButton('Отмена'))

        await callback.bot.send_message(callback.from_user.id, f'Оставьте комментарий', reply_markup=k)

    # else:
    #     if answers is None:
    #         answers = [{"user_id": user.id, "answer": f"{answer}"}]
    #     else:
    #         answers.append({"user_id": user.id, "answer": f"{answer}"})
    #
    #     update_task_answers(task_id, answers)
    #
    #     await callback.bot.send_message(callback.from_user.id, f'Ответ записан. Спасибо)')


async def comment_task(mes: types.Message, state: FSMContext):

    data = await state.get_data()

    task_id = data.get('task_id')
    task = get_periodic_task(task_id)

    answer = data.get('answer')

    answers = get_periodic_task_answers(task_id)

    user = get_worker_by_userid(mes.from_user.id)

    if mes.content_type == 'text':
        value = mes.text
    elif mes.content_type == 'photo':
        value = mes.photo[-1].file_id

    create_periodic_task_answer(task_id, user.id, answer, mes.content_type, value)

    await mes.answer('Ответ записан. Спасибо)', reply_markup=main_menu())

    await state.finish()
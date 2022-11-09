
from aiogram import types
from aiogram.dispatcher import FSMContext

from boards import week_days, main_menu
from db.operations import get_periodic_tasks, \
    get_periodic_task, \
    get_user, \
    get_periodic_task_users, \
    delete_periodic_task, get_task_users, get_periodic_task_answers, get_periodic_task_user_answer

from states import DeleteTask


async def periodic_tasks_list(mes: types.Message):
    tasks = get_periodic_tasks()

    k = types.InlineKeyboardMarkup()

    for task in tasks:
        k.add(types.InlineKeyboardButton(task.title, callback_data=f"inf_p_task {task.id}"))

    await mes.answer("Список периодичных задач", reply_markup=k)


async def periodic_task(callback: types.CallbackQuery):
    data = callback.data
    await callback.answer()

    task_id = data.split(' ')[1]

    task = get_periodic_task(task_id)

    k = types.InlineKeyboardMarkup()

    k.add(types.InlineKeyboardButton('Ответы', callback_data=f'answers_p_task {task.id}'))
    k.add(types.InlineKeyboardButton('Удалить', callback_data=f'delete_p_task {task.id}'))

    worker_list = ""
    counter = 1

    task_users = get_periodic_task_users(task.id)

    for task_user in task_users:
        worker = get_user(task_user.worker_id)
        worker_list += f"\n         {counter}. {worker.username}"
        counter += 1

    days_list = ""
    counter = 1

    for day in task.get_days_list():
        days_list += f"\n           {counter}. {week_days[int(day)-1]}"
        counter += 1

    times_list = ""
    counter = 1

    for time in task.get_times_list():
        times_list += f"\n          {counter}. {time}:00"
        counter += 1

    await callback.bot.send_message(callback.from_user.id,
                                          f"""
Название: {task.title}
Описание: {task.description}
Дни: {days_list}
Времена: {times_list}
Назначенные работники: {worker_list}""",
                                          reply_markup=k)


async def delete_task(callback: types.CallbackQuery):

    await callback.answer()

    task = get_periodic_task(callback.data.split(' ')[1])

    k = types.InlineKeyboardMarkup()

    k.row(types.InlineKeyboardButton('Да', callback_data=f'delete_task_ans yes {task.id}'), types.InlineKeyboardButton('Нет', callback_data=f'delete_task_ans no'))

    await callback.bot.send_message(callback.from_user.id, f"Вы уверены что хотите удалить задание \"{task.title}\"?", reply_markup=k)

    await DeleteTask.confirm.set()


async def delete_task_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split(' ')
    await callback.answer()

    answer = data[1]

    if answer == 'yes':

        try:
            task_id = data[2]
            delete_periodic_task(task_id)

            await callback.bot.send_message(callback.from_user.id, f"Задача успешно удалена")

        except Exception as e:

            await callback.bot.send_message(callback.from_user.id, f"Какая то ошибка (")
            raise e

        await state.finish()

    elif answer == 'no':

        await callback.bot.send_message(callback.from_user.id, f"Отмена", reply_markup=main_menu())

        await state.finish()


async def task_answers(callback: types.CallbackQuery):

    await callback.answer()

    data = callback.data.split(' ')

    task_id = data[1]

    task = get_periodic_task(task_id)

    task_answers = get_periodic_task_answers(task_id)

    send_text = f"Ответы на задание \"{task.title}\""

    answers_yes = []
    answers_no = []

    if task_answers == None:
        await callback.bot.send_message(callback.from_user.id, "Нету ответов")
        return

    for answer in task_answers:
        if answer.answer == 'yes':
            answers_yes.append(answer)
        else:
            answers_no.append(answer)

    send_text += "\nПоложительные ответы:"

    if len(answers_yes) > 0:

        counter = 1
        for answer in answers_yes:
            send_text += f"\n        {counter}. {get_user(answer['user_id']).username} /ptask_comment_{task_id}_{answer.user_id}"
            counter += 1
    else:
        send_text += "\n        Нету"

    send_text += "\nОтрицательные ответы:"

    if len(answers_no) > 0:
        counter = 1
        for answer in answers_no:
            send_text += f"\n        {counter}. {get_user(answer['user_id']).username} /ptask_comment_{task_id}_{answer.user_id}"
            counter += 1
    else:
        send_text += "\n        Нету"

    task_users = get_periodic_task_users(task_id)

    task_users = [get_user(task_user.worker_id) for task_user in task_users]

    not_answered = []

    def user_is_answered(user, answers_list):
        for answer in answers_list:
            if user.id == answer.user_id:
                return True

        return False

    for task_user in task_users:
        if user_is_answered(task_user, task_answers):
            continue
        else:
            not_answered.append(task_user)

    send_text += "\nНе ответившие:"

    if len(not_answered) > 0:
        counter = 1
        for answer in not_answered:
            send_text += f"\n        {counter}. {answer.username}"
            counter += 1
    else:
        send_text += "\n        Нету"

    await callback.bot.send_message(callback.from_user.id, send_text)


async def periodic_task_comment(mes: types.Message):
    data = mes.text.split('_')

    task_id = data[2]
    user_id = data[3]

    task = get_periodic_task(task_id)
    user = get_user(user_id)

    user_comment = get_periodic_task_user_answer(task_id, user_id)

    if user_comment:

        if user_comment.answer_type == 'text':
            send_text = f'Пользователь {user.username} оставил текстовое сообщение'
            await mes.answer(send_text)

            await mes.answer(user_comment.answer_value)

        elif user_comment.answer_type == 'photo':
            send_text = f'Пользователь {user.username} оставил фотографию'
            await mes.answer(send_text)

            await mes.answer_photo(user_comment.answer_value)

    else:
        await mes.answer('Ошибочка(... нету комментария')

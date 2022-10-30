from aiogram import types
from aiogram.dispatcher import Dispatcher

from states import *

from aiogram_calendar import simple_cal_callback

from .start import user_start,\
    add_admin,\
    ask_password,\
    ask_admin_username,\
    add_worker,\
    ask_user_username,\
    add_task,\
    add_task_title,\
    add_task_des,\
    process_simple_calendar,\
    add_task_time,\
    add_task_workers,\
    add_task_confirm,\
    cancel_btn, \
    answer_to_task, \
    comment_task



def setup(dp: Dispatcher):
    dp.register_message_handler(cancel_btn, lambda mes: mes.text == 'Отмена', state='*')
    dp.register_message_handler(user_start, commands=['start'])
    dp.register_message_handler(add_admin, commands=['add_admin'])
    dp.register_message_handler(ask_password, state=RequirePasswordState.password)
    dp.register_message_handler(ask_admin_username, state=RegisterAdminState.username)
    dp.register_message_handler(add_worker, lambda m: m.text == 'Добавить работника')
    dp.register_message_handler(ask_user_username, state=RegisterWorkerState.username)
    dp.register_message_handler(add_task, lambda m: m.text == 'Добавить одноразовую задачу')
    dp.register_message_handler(add_task_title, state=AddOneTimeTask.title)
    dp.register_message_handler(add_task_des, state=AddOneTimeTask.description)
    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(), state=AddOneTimeTask.day)
    dp.register_callback_query_handler(add_task_time, state=AddOneTimeTask.time)
    dp.register_callback_query_handler(add_task_workers, state=AddOneTimeTask.workers)
    dp.register_message_handler(add_task_confirm, state=AddOneTimeTask.confirm)

    dp.register_callback_query_handler(answer_to_task, lambda c:c.data.startswith('ans_to_o_t'))

    dp.register_message_handler(comment_task, state=TaskAnswer.comment, content_types=types.ContentType.all())


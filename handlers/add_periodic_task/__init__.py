from aiogram import types
from aiogram.dispatcher import Dispatcher

from states import *

from aiogram_calendar import simple_cal_callback

from .add_periodic_task import add_task,\
    add_task_title,\
    add_task_des,\
    process_simple_calendar,\
    add_task_time,\
    add_task_workers,\
    add_task_confirm,\
    answer_to_task, \
    comment_task



def setup(dp: Dispatcher):
    dp.register_message_handler(add_task, lambda m: m.text == 'Добавить периодичную задачу')
    dp.register_message_handler(add_task_title, state=AddPeriodicTask.title)
    dp.register_message_handler(add_task_des, state=AddPeriodicTask.description)
    dp.register_callback_query_handler(process_simple_calendar, state=AddPeriodicTask.days)
    dp.register_callback_query_handler(add_task_time, state=AddPeriodicTask.times)
    dp.register_callback_query_handler(add_task_workers, state=AddPeriodicTask.workers)
    dp.register_message_handler(add_task_confirm, state=AddPeriodicTask.confirm)

    dp.register_callback_query_handler(answer_to_task, lambda c: c.data.startswith('ans_to_p_t'))
    dp.register_message_handler(comment_task, state=TaskAnswer.comment, content_types=types.ContentType.all())
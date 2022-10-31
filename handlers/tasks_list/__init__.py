
from aiogram.dispatcher import Dispatcher

from states import *


from .tasks_list import periodic_tasks_list,\
    periodic_task,\
    delete_task,\
    delete_task_confirm,\
    task_answers

from .onetime_tasks import onetime_tasks_list,\
    onetime_task,\
    delete_onetime_task,\
    delete_onetime_task_confirm,\
    onetimetask_answers, \
    task_comment


def setup(dp: Dispatcher):
    dp.register_message_handler(periodic_tasks_list, lambda m: m.text == 'Список периодичных задач')
    dp.register_callback_query_handler(periodic_task, lambda c: c.data.startswith('inf_p_task'))
    dp.register_callback_query_handler(task_answers, lambda c: c.data.startswith('answers_p_task'))
    dp.register_callback_query_handler(delete_task, lambda c: c.data.startswith('delete_p_task'))
    dp.register_callback_query_handler(delete_task_confirm, state=DeleteTask.confirm)

    dp.register_message_handler(onetime_tasks_list, lambda m: m.text == 'Список одноразовых задач')
    dp.register_callback_query_handler(onetime_task, lambda c: c.data.startswith('inf_o_task'))
    dp.register_callback_query_handler(onetimetask_answers, lambda c: c.data.startswith('answers_o_task'))
    dp.register_callback_query_handler(delete_onetime_task, lambda c: c.data.startswith('delete_o_task'))
    dp.register_callback_query_handler(delete_onetime_task_confirm, state=DeleteOneTimeTask.confirm)

    dp.register_message_handler(task_comment, lambda mes: mes.startswith('/task_comment'))
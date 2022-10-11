
from aiogram.dispatcher import Dispatcher

from states import *

from .worker import *

def setup(dp: Dispatcher):
    dp.register_message_handler(worker_onetime_tasks, lambda m: m.text == 'Мои одноразовые задачи')
    dp.register_callback_query_handler(worker_o_task_info, lambda c: c.data.startswith('worker_o_task_inf'))

    dp.register_message_handler(worker_periodic_tasks, lambda m: m.text == 'Мои периодичные задачи')
    dp.register_callback_query_handler(worker_p_task_info, lambda c: c.data.startswith('worker_p_task_inf'))

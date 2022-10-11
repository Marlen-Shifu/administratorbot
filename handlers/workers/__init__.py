
from aiogram.dispatcher import Dispatcher

from states import *

from .workers import *

def setup(dp: Dispatcher):
    dp.register_message_handler(workers_list, lambda m: m.text == 'Список работников')
    dp.register_callback_query_handler(delete_worker_confirm, lambda c: c.data.startswith('delete_worker'))
    dp.register_callback_query_handler(delete_worker_answer, state=DeleteWorker.confirm)

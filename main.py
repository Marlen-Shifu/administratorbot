import asyncio
import datetime

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor

import logging
from config import BOT_TOKEN, POSITIONS

# celery -A celery_bot worker -l INFO -P threads
# celery -A celery_bot worker -l INFO --concurrency 1 -P threads
# celery -A celery_bot worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair -P solo
# celery -A celery_bot worker -l info --concurrency 1 -P gevent
from db.operations import add_user, create_periodic_task, create_task

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def start():
    import handlers
    handlers.start.setup(dp)
    handlers.add_periodic_task.setup(dp)
    handlers.tasks_list.setup(dp)
    handlers.worker.setup(dp)
    handlers.workers.setup(dp)
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    add_user("Marlen45", POSITIONS.ADMIN, id=840647074)

    add_user("Marlen45", POSITIONS.WORKER, id=840647074)
    add_user("Marlen45", POSITIONS.WORKER, id=840647074)


    # create_periodic_task(
    #     title='Отчет прихода на работу',
    #     description='Пусто',
    #     days=[0, 1, 2, 3, 4],
    #     times=['11:00'],
    #     creator_id=1,
    #     workers_list=[1]
    # )
    #
    # create_periodic_task(
    #     title='Отчет ухода с работы',
    #     description='Пусто',
    #     days=[0, 1, 2, 3, 4],
    #     times=['17:00'],
    #     creator_id=1,
    #     workers_list=[1]
    # )

    # create_task(
    #     title = 'Onetimetask1',
    #     description="Пусто",
    #     date = "2022-10-13",
    #     time = "15:00",
    #     creator_id=1,
    #     workers_list=[1, 2]
    # )
    #
    # create_task(
    #     title = 'Onetimetask2',
    #     description="Пусто",
    #     date = "2022-10-13",
    #     time = "14:00",
    #     creator_id=1,
    #     workers_list=[1, 2]
    # )

    start()
import datetime

from aiogram import types

import celery
from celery import Celery
from celery.schedules import crontab

from db.models import User, OneTimeTaskUser, PeriodicTask, PeriodicTaskUser, db_session as s

from db.operations import get_task, get_task_users, get_user, get_periodic_task, get_periodic_tasks, \
    update_task_answers, get_all_task_answers, get_onetime_tasks, get_onetime_task_answers, get_periodic_task_answers, \
    get_periodic_task_users

from utils.mailing.mail import mail, mail_document

import csv

import pandas as pd

app = Celery('tasks', broker='redis://:RedisPass@redis:6379/0', backend='redis://:RedisPass@redis:6379/1')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    # sender.add_periodic_task(crontab(minute=0, hour='*/1'), mail_service.s())
    # sender.add_periodic_task(5.0, mail_service.s())
    sender.add_periodic_task(10.0, mail_service.s())


# app.conf.beat_schedule = {
#     'mail-service': {
#         'task': 'tasks.mail_service',
#         'schedule': 10.0,
#     },
#     'test': {
#         'task': 'tasks.test',
#         'schedule': 10.0,
#         'args': ('hello',)
#     }
# }


@app.task(max_retries=10, default_retry_delay=3)
def mail_service():
    try:

        tasks = get_periodic_tasks()

        offset = datetime.timedelta(hours=6)
        timez = datetime.timezone(offset)

        now = datetime.datetime.now(tz=timez)

        week_day = now.weekday() + 1
        hour = now.hour

        if len(str(hour)) == 1:
            hour = "0" + str(hour)

        for task in tasks:
            if str(week_day) in task.get_days_list() and str(hour) in task.get_times_list():

                task_users = s.query(PeriodicTaskUser).filter_by(task_id=task.id).all()

                for task_user in task_users:
                    user = get_user(task_user.worker_id)

                    k = types.InlineKeyboardMarkup()

                    k.row(types.InlineKeyboardButton('Да', callback_data=f'ans_to_p_t yes {task.id}'),
                          types.InlineKeyboardButton('Нет', callback_data=f'ans_to_p_t no {task.id}'))

                    mail(user.user_id, f"Вы выполнили это задание?\nНазвание: {task.title}", reply_markup=k)

                periodic_task_answers.apply_async([task.id],
                                                  eta=datetime.datetime.now() + datetime.timedelta(seconds=5))

    except Exception as e:
        print(e)


@app.task(max_retries=10, default_retry_delay=3)
def periodic_task_answers(task_id):
    try:

        task = get_periodic_task(task_id)

        creator = get_user(task.creator_id)

        task_answers = task.get_answers()

        send_text = f"Ответы на задание \"{task.title}\""

        answers_yes = []
        answers_no = []

        if task_answers == None:
            mail(creator.user_id, "Ответов нет")
            return

        for answer in task_answers:
            if answer['answer'] == 'yes':
                answers_yes.append(answer)
            else:
                answers_no.append(answer)

        send_text += "\nПоложительные ответы:"

        if len(answers_yes) > 0:

            counter = 1
            for answer in answers_yes:
                send_text += f"\n        {counter}. {get_user(answer['user_id']).username} /ptask_comment_{task_id}_{answer['user_id']}"
                counter += 1
        else:
            send_text += "\n        Нету"

        send_text += "\nОтрицательные ответы:"

        if len(answers_no) > 0:
            counter = 1
            for answer in answers_no:
                send_text += f"\n        {counter}. {get_user(answer['user_id']).username} /ptask_comment_{task_id}_{answer['user_id']}"
                counter += 1
        else:
            send_text += "\n        Нету"

        task_users = get_task_users(task_id)

        task_users = [get_user(task_user.worker_id) for task_user in task_users]

        not_answered = []

        def user_is_answered(user, answers_list):
            for answer in answers_list:
                if user.id == answer['user_id']:
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
            for user in not_answered:
                send_text += f"\n        {counter}. {user.username}"
                counter += 1
        else:
            send_text += "\n        Нету"

        mail(creator.user_id, send_text)

        update_task_answers(task_id, [])

    except Exception as e:
        print(e)
        raise e


@app.task(bind=True, max_retries=10, default_retry_delay=3)
def ask_task(c_task, task_id, user_id):
    task = get_task(task_id)

    try:
        task_users = get_task_users(task_id)

        for task_user in task_users:
            user = get_user(task_user.worker_id)

            k = types.InlineKeyboardMarkup()

            k.row(types.InlineKeyboardButton('Да', callback_data=f'ans_to_o_t yes {task.id}'),
                  types.InlineKeyboardButton('Нет', callback_data=f'ans_to_o_t no {task.id}'))

            mail(user.user_id, f"Вы выполнили это задание?\nНазвание: {task.title}", reply_markup=k)

        s.remove()

        onetime_task_answers.apply_async([task_id], eta=datetime.datetime.now() + datetime.timedelta(minutes=30))

        return c_task.request.id
    except Exception as e:
        print(e)


@app.task(max_retries=10, default_retry_delay=3)
def onetime_task_answers(task_id):
    try:

        task = get_task(task_id)

        creator = get_user(task.creator_id)

        task_answers = task.get_answers()
        print(task_answers)

        send_text = f"Ответы на задание \"{task.title}\""

        answers_yes = []
        answers_no = []

        if task_answers == None:
            mail(creator.user_id, "Ответов нет")
            return

        for answer in task_answers:
            if answer['answer'] == 'yes':
                answers_yes.append(answer)
            else:
                answers_no.append(answer)

        send_text += "\nПоложительные ответы:"

        if len(answers_yes) > 0:

            counter = 1
            for answer in answers_yes:
                send_text += f"\n        {counter}. {get_user(answer['user_id']).username} /task_comment_{task_id}_{answer['user_id']}"
                counter += 1
        else:
            send_text += "\n        Нету"

        send_text += "\nОтрицательные ответы:"

        if len(answers_no) > 0:
            counter = 1
            for answer in answers_no:
                send_text += f"\n        {counter}. {get_user(answer['user_id']).username} /task_comment_{task_id}_{answer['user_id']}"
                counter += 1
        else:
            send_text += "\n        Нету"

        task_users = get_task_users(task_id)

        task_users = [get_user(task_user.worker_id) for task_user in task_users]

        not_answered = []

        def user_is_answered(user, answers_list):
            for answer in answers_list:
                print(user.id, answer['user_id'])
                if user.id == answer['user_id']:
                    return True

            return False

        for task_user in task_users:
            print(user_is_answered(task_user, task_answers))
            if user_is_answered(task_user, task_answers):
                continue
            else:
                not_answered.append(task_user)

        send_text += "\nНе ответившие:"

        if len(not_answered) > 0:
            counter = 1
            for user in not_answered:
                send_text += f"\n        {counter}. {user.username}"
                counter += 1
        else:
            send_text += "\n        Нету"

        mail(creator.user_id, send_text)

    except Exception as e:
        print(e)
        raise e


@app.task(bind=True, max_retries=10, default_retry_delay=3)
def ask_periodic_task(c_task, task_id, user_id):
    try:
        task = get_periodic_task(task_id)
        task_users = s.query(PeriodicTaskUser).filter_by(task_id=task_id).all()

        for task_user in task_users:
            user = get_user(task_user.worker_id)
            mail(user.user_id, f"Вы выполнили это задание?\nНазвание: {task.title}")

        s.remove()

        # run_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
        #
        # ask_periodic_task.apply_async((task_id, user_id), eta=run_time)

        return c_task.request.id
    except Exception as e:
        print(e)


@app.task(max_retries=10, default_retry_delay=3)
def tasks_report(user_id):
    try:

        today = datetime.datetime.today().date()

        writer = pd.ExcelWriter(f'{today}_report.xlsx', engine='xlsxwriter')

        tasks = get_onetime_tasks()

        today_tasks = []

        for task in tasks:
            if task.time.date() == today:
                today_tasks.append(task)

        onetime_tasks_report_write(writer, today_tasks)

        p_tasks = get_periodic_tasks()

        today_p_tasks = []

        for task in p_tasks:
            if str(today.weekday() + 1) in task.get_days_list():
                today_p_tasks.append(task)

        mail(user_id, f'{today_p_tasks}')

        periodic_tasks_report_write(writer, today_p_tasks)

        writer.save()
        with open(f'{today}_report.xlsx', 'rb') as file:
            mail_document(user_id, file)

        # with open(f'{today}_report.csv', 'w') as file:
        #     writer = csv.writer(file)
        #
        #     for task in today_tasks:
        #         writer.writerow([task.id, task.title, task.description, task.time, task.creator_id])
        # with open(f'{today}_report.csv', 'rb') as file:
        #     mail_document(840647074, file)



    except Exception as e:
        print(e)
        raise e


def onetime_tasks_report_write(writer, tasks_list):
    titles = []
    dess = []
    times = []
    workers = []
    answers_yes = []
    answers_no = []
    answers_not = []

    def add_row(title=None, des=None, time=None, worker=None, answer_yes=None, answer_no=None, answer_not=None):
        titles.append(title)
        dess.append(des)
        times.append(time)
        workers.append(worker)
        answers_yes.append(answer_yes)
        answers_no.append(answer_no)
        answers_not.append(answer_not)

    for task in tasks_list:

        task_answers = get_onetime_task_answers(task.id)

        add_row(task.title, task.description, str(task.time))

        for task_answer in task_answers:
            worker = get_user(task_answer.user_id)

            if task_answer.answer == 'yes':
                add_row(worker=worker.username, answer_yes='+')
            elif task_answer.answer == 'no':
                add_row(worker=worker.username, answer_no='-')

        task_users = get_task_users(task.id)

        task_users = [get_user(task_user.worker_id) for task_user in task_users]

        def user_is_answered(user, answers_list):
            for answer in answers_list:
                if user.id == answer.user_id:
                    return True

            return False

        for task_user in task_users:
            if user_is_answered(task_user, task_answers):
                continue
            else:
                add_row(worker=task_user.username, answer_not='?')

    df = pd.DataFrame({'Название': titles, 'Описание': dess, 'Время': times, 'Работник': workers, 'Да': answers_yes,
                       'Нет': answers_no, 'Нет ответа': answers_not})

    df.to_excel(writer, sheet_name='Одноразовые задачи', index=False)


def periodic_tasks_report_write(writer, tasks_list):
    titles = []
    dess = []
    times = []
    workers = []
    answers_yes = []
    answers_no = []
    answers_not = []

    def add_row(title=None, des=None, time=None, worker=None, answer_yes=None, answer_no=None, answer_not=None):
        titles.append(title)
        dess.append(des)
        times.append(time)
        workers.append(worker)
        answers_yes.append(answer_yes)
        answers_no.append(answer_no)
        answers_not.append(answer_not)

    for task in tasks_list:
        task_answers = get_periodic_task_answers(task.id)
        for time in task.get_times_list():
            add_row(task.title, task.description, time)

            for task_answer in task_answers:
                mail(840647074, f"{time}")
                mail(840647074, f"{task_answer.time.hour}")
                if int(time) == task_answer.time.hour:

                    worker = get_user(task_answer.user_id)

                    if task_answer.answer == 'yes':
                        add_row(worker=worker.username, answer_yes='+')
                    elif task_answer.answer == 'no':
                        add_row(worker=worker.username, answer_no='-')



        # task_users = get_periodic_task_users(task.id)
        #
        # task_users = [get_user(task_user.worker_id) for task_user in task_users]
        #
        # def user_is_answered(user, answers_list):
        #     for answer in answers_list:
        #         if user.id == answer.user_id:
        #             return True
        #
        #     return False
        #
        # for task_user in task_users:
        #     if user_is_answered(task_user, task_answers):
        #         continue
        #     else:
        #         add_row(worker=task_user.username, answer_not='?')

    df = pd.DataFrame({'Название': titles, 'Описание': dess, 'Время': times, 'Работник': workers, 'Да': answers_yes,
                       'Нет': answers_no, 'Нет ответа': answers_not})

    df.to_excel(writer, sheet_name='Периодичные задачи', index=False)

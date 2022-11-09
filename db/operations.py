import datetime

from .models import *
from config import POSITIONS

import asyncio

from db.models import db_session as s

def get_user(id, username = None):

    try:
        user = s.query(User).filter_by(id = id).first()

        if user == None:
            user_by_username = s.query(User).filter_by(username = username).first()
            return user_by_username

        return user
    except Exception as e:
        print(e)


def get_user_by_userid(id):

    try:
        user = s.query(User).filter_by(user_id = id).first()

        return user
    except Exception as e:
        print(e)

def get_worker_by_userid(id):

    try:
        user = s.query(User).filter_by(user_id = id, position = POSITIONS.WORKER).first()

        return user
    except Exception as e:
        print(e)

def add_user(username, position, id=None):

    try:

        user = User(username = username, position = position, user_id = id)

        s.add(user)
        s.commit()

        return 'ok'

    except Exception as e:
        return 'no'


def update_user_id(user, id):

    try:
        s.query(User).filter_by(username = user.username).update({User.user_id: id})
        s.commit()
    except Exception as e:
        print(e)


def get_all_workers():

    try:
        workers = s.query(User).filter_by(position = POSITIONS.WORKER).all()
        return workers
    except Exception as e:
        print(e)


# class OneTimeTask(Base):
#     __tablename__ = 'onetime_tasks'
#
#     id = Column(Integer, primary_key=True)
#     task_id = Column(String(255))
#     time = Column(DateTime())
#     creator_id = Column(Integer)
#
#
# class OneTimeTaskUser(Base):
#     __tablename__ = 'onetimetask_user'
#
#     id = Column(Integer, primary_key=True)
#
#     task_id = Column(Integer)
#     worker_id = Column(Integer)


def get_task(id):

    try:
        task = s.query(OneTimeTask).filter_by(id = id).first()

        return task
    except Exception as e:
        print(e)
        return 'no'


def get_onetime_tasks():

    try:
        tasks = s.query(OneTimeTask).all()
        return tasks
    except Exception as e:
        print(e)


def get_onetime_task_users(task_id):
    try:
        res = s.query(OneTimeTaskUser).filter_by(task_id=task_id).all()
        return res
    except Exception as e:
        print(e)


def update_celery_task_id(task_id, new_celery_task_id):

    try:
        task = get_task(task_id)
        task.task_id = str(new_celery_task_id)
        s.commit()
    except Exception as e:
        print(e)
        raise e




def get_periodic_task(id):

    try:
        task = s.query(PeriodicTask).filter_by(id = id).first()

        return task
    except Exception as e:
        print(e)
        return 'no'

def get_task_users(task_id):

    try:
        task_users = s.query(OneTimeTaskUser).filter_by(task_id=task_id).all()

        return task_users
    except Exception as e:
        print(e)
        return 'no'


def create_task(title, description, date, time, creator_id, workers_list):

    try:

        date_time = datetime.datetime.strptime(date + ", " + time, "%Y-%m-%d, %H:%M")

        task = OneTimeTask(
            title = title,
            description = description,
            time = date_time,
            creator_id = creator_id
        )

        s.add(task)
        s.flush()

        for worker_id in workers_list:

            task_user = OneTimeTaskUser(
                task_id = task.id,
                worker_id = worker_id
            )
            s.add(task_user)
            s.flush()
            s.commit()

        s.commit()

        return task.id

    except Exception as e:
        print(e)
        return 'no'


def create_periodic_task(title, description, days, times, creator_id, workers_list, answers = None):

    try:

        task_days = ''

        for day in days:
            task_days += f' {int(day)+1}'

        task_times = ''

        for time in times:
            task_times += f' {time.split(":")[0]}'

        task = PeriodicTask(
            title = title,
            description = description,
            days = task_days,
            times = task_times,
            creator_id = creator_id,
            answers = answers
        )

        s.add(task)
        s.flush()

        for worker_id in workers_list:

            task_user = PeriodicTaskUser(
                task_id = task.id,
                worker_id = worker_id
            )
            s.add(task_user)
            s.flush()
            s.commit()

        s.commit()

        return task.id

    except Exception as e:
        print(e)
        return 'no'


def get_periodic_tasks():

    try:
        tasks = s.query(PeriodicTask).all()
        return tasks
    except Exception as e:
        print(e)


def delete_periodic_task(task_id):
    try:
        task = get_periodic_task(task_id)
        s.delete(task)
        s.commit()
    except Exception as e:
        print(e)
        raise e


def get_periodic_task_users(task_id):
    try:
        res = s.query(PeriodicTaskUser).filter_by(task_id=task_id).all()
        return res
    except Exception as e:
        print(e)


def update_task_answers(task_id, new_answers):

    try:
        task = get_periodic_task(task_id)
        task.answers = str(new_answers).replace("'", '"')
        s.commit()
    except Exception as e:
        print(e)
        raise e


def update_onetime_task_answers(task_id, new_answers):

    try:
        task = get_task(task_id)
        task.answers = str(new_answers).replace("'", '"')
        s.commit()
    except Exception as e:
        print(e)
        raise e


def delete_onetime_task_oper(task_id):
    try:
        task = get_task(task_id)
        s.delete(task)
        s.commit()
    except Exception as e:
        print(e)
        raise e
# create_periodic_task("Marlen45", POSITIONS.ADMIN, id=840647074)
# create_periodic_task("Marlen45", POSITIONS.WORKER, id=840647074)

def get_all_onetime_task_users():
    try:
        res = s.query(OneTimeTaskUser).all()

        return res
    except Exception as e:
        print(e)
        raise e

def get_onetime_task_users_of_user(user_id):
    try:
        res = s.query(OneTimeTaskUser).filter_by(worker_id = user_id)

        return res
    except Exception as e:
        print(e)
        raise e


def get_onetime_tasks_of_user(user_id):
    try:

        task_users = get_onetime_task_users_of_user(user_id)

        user_tasks = [get_task(user_task_user.task_id) for user_task_user in task_users]

        return user_tasks

    except Exception as e:
        print(e)
        raise e


def get_periodic_task_users_of_user(user_id):
    try:
        res = s.query(PeriodicTaskUser).filter_by(worker_id = user_id)

        return res
    except Exception as e:
        print(e)
        raise e


def get_periodic_tasks_of_user(user_id):
    try:

        task_users = get_periodic_task_users_of_user(user_id)

        user_tasks = [get_periodic_task(user_task_user.task_id) for user_task_user in task_users]

        return user_tasks

    except Exception as e:
        print(e)
        raise e


def delete_worker(worker_id):
    try:
        worker = get_user(worker_id)
        s.delete(worker)
        s.commit()
    except Exception as e:
        print(e)
        raise e


def get_onetime_task_answers(task_id):
    try:
        answers = s.query(OneTimeTaskAnswer).filter_by(task_id = task_id)

        return answers
    except Exception as e:
        print(e)
        raise e

def get_periodic_task_answers(task_id):
    try:
        answers = s.query(PeriodicTaskAnswer).filter_by(task_id = task_id)

        return answers
    except Exception as e:
        print(e)
        raise e

def create_onetime_task_answer(task_id, user_id, answer,type, value):
    try:

        ins = OneTimeTaskAnswer(
            task_id = task_id,
            user_id = user_id,
            answer = answer,
            answer_type = type,
            answer_value = value
        )

        s.add(ins)
        s.commit()

    except Exception as e:
        print(e)
        raise e


def create_periodic_task_answer(task_id, user_id, answer,type, value):
    try:

        ins = PeriodicTaskAnswer(
            task_id = task_id,
            user_id = user_id,
            answer = answer,
            answer_type = type,
            answer_value = value
        )

        s.add(ins)
        s.commit()

    except Exception as e:
        print(e)
        raise e



def get_onetime_task_user_answer(task_id, user_id):
    try:
        answer = s.query(OneTimeTaskAnswer).filter_by(task_id = task_id, user_id = user_id).first()

        return answer
    except Exception as e:
        print(e)
        raise e


def get_periodic_task_user_answer(task_id, user_id):
    try:
        answer = s.query(PeriodicTaskAnswer).filter_by(task_id = task_id, user_id = user_id).first()

        return answer
    except Exception as e:
        print(e)
        raise e


def get_all_task_answers(task_id, user_id):
    try:
        answer = s.query(OneTimeTaskAnswer).filter_by(task_id = task_id, user_id = user_id).first()

        return answer
    except Exception as e:
        print(e)
        raise e

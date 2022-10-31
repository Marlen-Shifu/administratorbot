from sqlalchemy import create_engine, Column, Integer, String, func, DateTime, TEXT
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool

import json

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://admin:admin_password@database:5432/db'
engine = create_engine(DATABASE_CONNECTION_URI, echo=False, pool_recycle=3600, pool_size=10)


Base = declarative_base()

db_session = scoped_session(sessionmaker(bind=engine))



class User(Base):
    __tablename__ = 'registered_users'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=True)
    username = Column(String(255))
    position = Column(String(255))


class OneTimeTask(Base):
    __tablename__ = 'onetime_tasks'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255))
    title = Column(String(255))
    description = Column(TEXT)
    time = Column(DateTime())
    creator_id = Column(Integer)
    answers = Column(TEXT, nullable=True)

    def get_answers(self):
        if self.answers != None:
            return json.loads(self.answers)
        else:
            return None

    def is_user_answered(self, user_id):
        answers = self.get_answers()

        if answers == None:
            return False

        for answer in answers:
            if answer['user_id'] == user_id:
                return True

        return False

    def get_user_comment(self, user_id):

        answers = self.get_answers()

        if answers == None:
            return None

        for answer in answers:
            if answer['user_id'] == user_id:
                return answer

        return None


class OneTimeTaskUser(Base):
    __tablename__ = 'onetimetask_user'

    id = Column(Integer, primary_key=True)

    task_id = Column(Integer)
    worker_id = Column(Integer)


class PeriodicTask(Base):
    __tablename__ = 'periodic_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255))
    title = Column(String(255))
    description = Column(TEXT)
    days = Column(String(255))
    times = Column(String(255))
    creator_id = Column(Integer)
    answers = Column(TEXT, nullable=True)

    def get_times_list(self):

        return self.times.strip().split(' ')

    def get_days_list(self):

        return self.days.strip().split(' ')

    def get_answers(self):
        if self.answers != None:
            return json.loads(self.answers)
        else:
            return None

    def is_user_answered(self, user_id):
        answers = self.get_answers()

        if answers == None:
            return False

        for answer in answers:
            if answer['user_id'] == user_id:
                return True

        return False


class PeriodicTaskUser(Base):
    __tablename__ = 'periodictask_user'

    id = Column(Integer, primary_key=True)

    task_id = Column(Integer)
    worker_id = Column(Integer)


Base.metadata.create_all(engine)
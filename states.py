from aiogram.dispatcher.filters.state import State, StatesGroup


class RequirePasswordState(StatesGroup):
    password = State()


class RegisterAdminState(StatesGroup):
    username = State()


class RegisterWorkerState(StatesGroup):
    username = State()


class AddOneTimeTask(StatesGroup):
    title = State()
    description = State()
    day = State()
    time = State()
    workers = State()
    confirm = State()


class AddPeriodicTask(StatesGroup):
    title = State()
    description = State()

    choose_schedule_type = State()

    days = State()

    work_days_count = State()
    rest_days_count = State()

    times = State()
    workers = State()
    confirm = State()


class DeleteTask(StatesGroup):
    confirm = State()


class DeleteOneTimeTask(StatesGroup):
    confirm = State()


class DeleteWorker(StatesGroup):
    confirm = State()


class TaskAnswer(StatesGroup):
    answer = State()
    comment = State()


class PeriodicTaskAnswer(StatesGroup):
    answer = State()
    comment = State()
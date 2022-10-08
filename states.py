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
    days = State()
    times = State()
    workers = State()
    confirm = State()


class DeleteTask(StatesGroup):
    confirm = State()
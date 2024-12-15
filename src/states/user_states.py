from aiogram.fsm.state import State, StatesGroup


class User(StatesGroup):
    wait_phone_number = State()
    age_poll = State()
    poll1 = State()
    poll2 = State()
    poll3 = State()
    poll4 = State()
    poll5 = State()
    poll6 = State()
    final = State()
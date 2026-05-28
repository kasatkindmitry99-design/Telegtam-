from aiogram.fsm.state import (StatesGroup,State)

class AdminStates(StatesGroup):

    find_user = State()

    broadcast = State()

    confirm_broadcast = State()
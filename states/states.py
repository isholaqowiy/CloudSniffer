from aiogram.fsm.state import State, StatesGroup

class DetectionStates(StatesGroup):
    WaitingForContent = State()

class AdminStates(StatesGroup):
    WaitingForBroadcast = State()

from dataclasses import dataclass
from typing import Optional

from src.settings import SECONDS_IN_MINUTE


WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20


@dataclass
class WorkingState:
    name: str
    title: str
    time: int
    next: Optional['WorkingState'] = None

    @classmethod
    def short_break(cls):
        return cls('break', 'Short break', SHORT_BREAK_MIN * SECONDS_IN_MINUTE)

    @classmethod
    def long_break(cls):
        return cls('long_break', 'Long break', LONG_BREAK_MIN * SECONDS_IN_MINUTE)

    @classmethod
    def workin(cls):
        return cls('work', 'Working', WORK_MIN * SECONDS_IN_MINUTE)


class WorkingStateMachine:
    def __init__(self, states: list[WorkingState]) -> None:
        self._start_state = self._current_state = self._connect_states(states)
        self.work_iteration_number = 0

    def _connect_states(self, states: list[WorkingState]) -> WorkingState:
        assert len(states), "Has to be at least one state"
        if len(states) == 1:
            return states[0]

        for ind in range(len(states) - 1):
            cur_state = states[ind]
            next_state = states[ind+1]
            cur_state.next = next_state
        states[-1].next = states[0]
        return states[0]

    def activate_state(self) -> WorkingState:
        return_state = self._current_state
        self._current_state = return_state.next
        
        if return_state.name == 'work':
            self.work_iteration_number += 1

        if return_state.name == 'long_break':
            self.work_iteration_number = 0

        return return_state

    def reset(self) -> WorkingState:
        self._current_state = self._start_state
        self.work_iteration_number = 0
        return self._current_state


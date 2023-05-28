import tkinter as tk

from dataclasses import dataclass
from typing import Optional

from pynotifier import NotificationClient, Notification
from pynotifier.backends import platform


# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"

DEFAULT = '#bedbbb'

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

SECONDS_IN_MINUTE = 60
MS_IN_SECOND = 1000


notify_client = NotificationClient()
notify_client.register_backend(platform.Backend())


def send_notification(text):
    print('Work Concentrator: ', text)
    notification = Notification(
        title='Work Scheduler',
        message=text,
    )
    notify_client.notify_all(notification)


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
        return self._current_state


title_color_mapping = {
    'break': PINK,
    'long_break': RED,
    'work': GREEN
}


# ---------------------------- UI SETUP ------------------------------- #
button_style = {
    'highlightthickness': 0,
    'pady': 10,
    'padx': 20,
    'font': (FONT_NAME, 14),
    'bg': DEFAULT
}

class UIBuilder():
    def __init__(self, state_machine: WorkingStateMachine):
        self.window = tk.Tk()
        self.canvas: Optional[tk.Canvas] = None
        self.timer_text: Optional[int] = None
        self.title_label: Optional[tk.Label] = None
        self.work_iterates_label: Optional[tk.Label] = None

        self.timer = None
        self.state_machine = state_machine

    def build(self) -> tk.Tk:
        self.window.title('Work scheduler')
        self.window.minsize(550, 300)
        self.window.config(padx=30, pady=40, bg=YELLOW)

        base_container = tk.Frame(self.window, bg=YELLOW)
        base_container.pack()

        self.title_label = tk.Label(base_container, text='Timer', bg=YELLOW, fg=GREEN,
                               font=(FONT_NAME, 30, 'bold'))
        self.title_label.grid(row=0, column=1)

        self.canvas = tk.Canvas(base_container, width=200, height=100, bg=YELLOW, highlightthickness=0)
        self.timer_text = self.canvas.create_text(100, 50,
                                        text='00:00', font=(FONT_NAME, 35, 'bold'))
        self.canvas.grid(row=1, column=1)

        start_button = tk.Button(base_container, text='Start', command=self._start_timer, **button_style)
        start_button.grid(row=2, column=0)

        end_button = tk.Button(base_container, text='Reset', command=self._reset_timer, **button_style)
        end_button.grid(row=2, column=2)

        self.work_iterates_label = tk.Label(base_container, text='Nope', fg=RED, bg=YELLOW)
        self.work_iterates_label.grid(row=3, column=1)

        base_container.grid_columnconfigure(0, weight=1)
        base_container.grid_columnconfigure(3, weight=1)

        return self.window

    def _reset_timer(self):
        if not self.timer:
            return

        window.after_cancel(self.timer)
        self.timer = None

        self.state_machine.reset()

        assert self.title_label
        assert self.work_iterates_label
        assert self.canvas
        assert self.timer_text
        self.title_label.config(text='Timer', fg=GREEN)
        self.work_iterates_label.config(text='Nope')
        self.canvas.itemconfig(self.timer_text, text='00:00')
        send_notification('Working circle was stopped')

    def _start_timer(self):
        global state_machine
        
        if self.timer:
            return

        current_state = self.state_machine.activate_state() 
        stages_text = '+ ' * state_machine.work_iteration_number
        assert self.work_iterates_label
        self.work_iterates_label.config(text=stages_text)

        send_notification(current_state.title)

        assert self.title_label
        self.title_label.config(
            text=current_state.title,
            fg=title_color_mapping[current_state.name]
        )
        self._count_down(current_state.time)

    def _count_down(self, count):
        minutes = count // 60
        seconds = count % 60
        assert self.timer_text
        assert self.canvas
        self.canvas.itemconfig(self.timer_text, text=f'{minutes}:{seconds:02}')

        if count > 0:
            self.timer = window.after(MS_IN_SECOND, self._count_down, count-1)
        else:
            self.timer = None
            self._start_timer()


if __name__ == '__main__':
    state_machine = WorkingStateMachine([
        WorkingState.workin(),
        WorkingState.short_break(),
        WorkingState.workin(),
        WorkingState.short_break(),
        WorkingState.workin(),
        WorkingState.short_break(),
        WorkingState.workin(),
        WorkingState.short_break(),
        WorkingState.long_break()
    ])
    window = UIBuilder(state_machine).build()
    window.mainloop()

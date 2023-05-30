import tkinter as tk
from typing import Optional

from src.state import WorkingStateMachine
from src.settings import MS_IN_SECOND
from src.notifier import WorkNotifier


PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
DEFAULT = '#bedbbb'

FONT_NAME = "Courier"


button_style = {
    'highlightthickness': 0,
    'pady': 10,
    'padx': 20,
    'font': (FONT_NAME, 14),
    'bg': DEFAULT
}


title_color_mapping = {
    'break': PINK,
    'long_break': RED,
    'work': GREEN
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
        self.notifier = WorkNotifier()

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

        self.window.after_cancel(self.timer)
        self.timer = None

        self.state_machine.reset()

        assert self.title_label
        assert self.work_iterates_label
        assert self.canvas
        assert self.timer_text
        self.title_label.config(text='Timer', fg=GREEN)
        self.work_iterates_label.config(text='Nope')
        self.canvas.itemconfig(self.timer_text, text='00:00')
        self.notifier.send('Working circle was stopped')

    def _start_timer(self):
        global state_machine
        
        if self.timer:
            return

        current_state = self.state_machine.activate_state() 
        stages_text = '+ ' * self.state_machine.work_iteration_number
        assert self.work_iterates_label
        self.work_iterates_label.config(text=stages_text)

        self.notifier.send(current_state.title)

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
            self.timer = self.window.after(MS_IN_SECOND, self._count_down, count-1)
        else:
            self.timer = None
            self._start_timer()

import tkinter as tk
import subprocess

from dataclasses import dataclass
from typing import Optional, List
from os import path

# from pynotifier import Notification


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

timer = None
# ---------------------------- TIMER RESET ------------------------------- #

def send_notification(text):
    print('Work Concentrator: ', text)
    # cur_directory = path.dirname(__file__) 
    # Notification(
    #     title='Work Scheduler',
    #     description=text,
    #     # On Windows .ico is required, on Linux - .png
    #     icon_path=path.join(cur_directory, 'media', 'icon.png'),
    #     duration=5 * 60,
    #     urgency=Notification.URGENCY_LOW
    # ).send()


def reset_timer():
    global timer
    global current_state

    if not timer:
        return

    window.after_cancel(timer)
    timer = None
    current_state = None
    title_label.config(text='Timer', fg=GREEN)
    work_iterates_label.config(text='Nope')
    canvas.itemconfig(timer_text, text='00:00')
    send_notification('Working circle was stopped')

# ---------------------------- TIMER MECHANISM ------------------------------- #


@dataclass
class WorkingState:
    name: str
    title: str
    time: int
    next: Optional['WorkingState'] = None

    @classmethod
    def short_break(cls):
        return cls('break', 'Short break', 3) # SHORT_BREAK_MIN * SECONDS_IN_MINUTE)

    @classmethod
    def long_break(cls):
        return cls('long_break', 'Long break', 6) # LONG_BREAK_MIN * SECONDS_IN_MINUTE)

    @classmethod
    def workin(cls):
        return cls('work', 'Working', 6) # WORK_MIN * SECONDS_IN_MINUTE)

    @staticmethod
    def connect_states(states: List['WorkingState']) -> 'WorkingState':
        if not len(states):
            return None
        if len(states) == 1:
            return states[0]

        for ind in range(len(states) - 1):
            cur_state = states[ind]
            next_state = states[ind+1]
            cur_state.next = next_state
        states[-1].next = states[0]
        return states[0]


start_state = WorkingState.connect_states([
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


current_state = None
passed_working_stages = 0
title_color_mapping = {
    'break': PINK,
    'long_break': RED,
    'work': GREEN
}

def start_timer():
    global current_state
    global passed_working_stages
    
    if timer:
        return

    if not current_state:
        current_state = start_state
    else:
        if current_state.name == 'work':
            passed_working_stages += 1
            stages_text = '+ ' * passed_working_stages
            work_iterates_label.config(text=stages_text)

        if current_state.name == 'long_break':
            passed_working_stages = 0
        current_state = current_state.next

    send_notification(current_state.title)

    title_label.config(
        text=current_state.title,
        fg=title_color_mapping[current_state.name]
    )
    count_down(current_state.time)

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #

def count_down(count):
    minutes = count // 60
    seconds = count % 60
    canvas.itemconfig(timer_text, text=f'{minutes}:{seconds:02}')

    global timer
    if count > 0:
        timer = window.after(1000, count_down, count-1)
    else:
        timer = None
        start_timer()

# ---------------------------- UI SETUP ------------------------------- #

button_style = {
    'highlightthickness': 0,
    'pady': 10,
    'padx': 20,
    'font': (FONT_NAME, 14),
    'bg': DEFAULT
}

window = tk.Tk()
window.title('Work scheduler')
window.minsize(550, 300)
window.config(padx=30, pady=40, bg=YELLOW)

base_container = tk.Frame(window, bg=YELLOW)
base_container.pack()

title_label = tk.Label(base_container, text='Timer', bg=YELLOW, fg=GREEN,
                       font=(FONT_NAME, 30, 'bold'))
title_label.grid(row=0, column=1)

canvas = tk.Canvas(base_container, width=200, height=100, bg=YELLOW, highlightthickness=0)
timer_text = canvas.create_text(100, 50,
                                text='00:00', font=(FONT_NAME, 35, 'bold'))
canvas.grid(row=1, column=1)

start_button = tk.Button(base_container, text='Start', command=start_timer, **button_style)
start_button.grid(row=2, column=0)

end_button = tk.Button(base_container, text='Reset', command=reset_timer, **button_style)
end_button.grid(row=2, column=2)

work_iterates_label = tk.Label(base_container, text='Nope', fg=RED, bg=YELLOW)
work_iterates_label.grid(row=3, column=1)

base_container.grid_columnconfigure(0, weight=1)
base_container.grid_columnconfigure(3, weight=1)

window.mainloop()
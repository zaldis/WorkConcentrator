import tkinter as tk


def set_full_screen_app(window: tk.Tk) -> None:
    window.state('normal')
    window.attributes('-fullscreen', True)


def set_minimize_screen_app(window: tk.Tk) -> None:
    window.state('icon')
    window.attributes('-fullscreen', False)

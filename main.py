from src.state import WorkingState, WorkingStateMachine
from src.ui import UIBuilder


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
        WorkingState.workin(),
        WorkingState.long_break()
    ])
    window = UIBuilder(state_machine).build()
    window.mainloop()

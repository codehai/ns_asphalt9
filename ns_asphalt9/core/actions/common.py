import time
from ..controller import pro, Buttons
from .. import globals


def connect_controller():
    """连接手柄"""
    pro.press_buttons([Buttons.L, Buttons.R], down=1)
    time.sleep(1)
    pro.press_buttons([Buttons.A], down=0.5)


def demoted():
    """降级"""
    globals.DIVISION = ""
    pro.press_button(Buttons.B, 3)


def set_eng():
    pass


def system_error():
    pro.press_group([Buttons.A] * 3, 3)
    globals.task_queue.put(globals.CONFIG["模式"])

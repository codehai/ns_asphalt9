import datetime
import shutil
import threading
import time
import traceback


from core import consts, globals
from core.controller import Buttons, pro
from core.ocr import ocr_screen
from core.pages import Page

from core.tasks import TaskManager
from core.utils.log import logger
from core.gui.app import App


def process_screen(page: Page):
    """根据显示内容执行动作"""

    if page.name != consts.empty and page.action:
        page.call_action()

    else:
        logger.info("Match none page.")
        globals.NO_OPERATION_COUNT += 1
        if globals.NO_OPERATION_COUNT > 30:
            logger.info("Keep alive press button y")
            pro.press_buttons(Buttons.Y)
            globals.NO_OPERATION_COUNT = 0


def capture():
    filename = "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
    shutil.copy("./images/output.jpg", f"./images/{filename}")
    return filename


def event_loop():
    TaskManager.task_init()

    while globals.G_RACE_RUN_EVENT.is_set() and globals.G_RUN.is_set():
        try:
            page = ocr_screen()
            if page.division:
                globals.DIVISION = page.division
            if page.mode:
                globals.MODE = page.mode
            dispatched = TaskManager.task_dispatch(page)
            if not dispatched:
                process_screen(page)
            time.sleep(3)
        except Exception as err:
            filename = capture()
            logger.error(
                f"Caught exception, err = {err}, traceback = {traceback.format_exc()}, \
                  filename = {filename}"
            )

    globals.G_RACE_QUIT_EVENT.set()


def start_app():
    app = App()
    app.mainloop()


def thread_start_app():
    t = threading.Thread(target=start_app, args=())
    t.start()


def main():
    globals.G_RACE_QUIT_EVENT.set()
    globals.G_RUN.set()
    thread_start_app()
    while globals.G_RUN.is_set():
        if globals.G_RACE_RUN_EVENT.is_set():
            event_loop()
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()

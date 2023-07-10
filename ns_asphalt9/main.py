import argparse
import datetime
import multiprocessing
import os
import shutil
import threading
import time
import traceback
import types

from .core import consts
from .core import globals as G
from .core.actions import (enter_carhunt, enter_game, enter_series, free_pack,
                           prix_pack)
from .core.controller import Buttons, pro
from .core.gui.app import App
from .core.ocr import ocr_screen
from .core.pages import Page
from .core.screenshot import screenshot
from .core.tasks import TaskManager
from .core.utils.log import logger


def process_screen(page: Page):
    """根据显示内容执行动作"""

    if page.name != consts.empty and page.action:
        page.call_action()

    else:
        logger.info("Match none page.")
        G.NO_OPERATION_COUNT += 1
        if G.NO_OPERATION_COUNT > 30:
            logger.info("Keep alive press button y")
            pro.press_buttons(Buttons.Y)
            G.NO_OPERATION_COUNT = 0


def capture():
    debug = os.environ.get("A9_DEBUG", 0)
    filename = "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
    if not debug:
        shutil.copy("./output.jpg", f"./{filename}")
    return filename


def event_loop():
    TaskManager.task_init()

    while G.G_RACE_RUN_EVENT.is_set() and G.G_RUN.is_set():
        try:
            page = ocr_screen()
            if page.division:
                G.DIVISION = page.division
            if page.mode:
                G.MODE = page.mode
            dispatched = TaskManager.task_dispatch(page)
            if not dispatched:
                process_screen(page)
            time.sleep(3)
        except Exception as err:
            # filename = capture()
            logger.error(
                f"Caught exception, err = {err}, traceback = {traceback.format_exc()}"
            )

    G.G_RACE_QUIT_EVENT.set()


def command_input(queue):
    while G.G_RUN.is_set():
        command = queue.get()

        if isinstance(command, str):
            if command == "stop":
                # 停止挂机
                if G.G_RACE_RUN_EVENT.is_set():
                    G.G_RACE_RUN_EVENT.clear()
                    logger.info("Stop event loop.")
                    G.G_RACE_QUIT_EVENT.wait()
                    logger.info("Event loop stoped.")
                else:
                    logger.info("Event loop not running.")

            elif command == "run":
                # 开始挂机
                if G.G_RACE_RUN_EVENT.is_set():
                    logger.info("Event loop is running.")
                else:
                    G.G_RACE_RUN_EVENT.set()
                    G.G_RACE_QUIT_EVENT.clear()
                    logger.info("Start run event loop.")

            elif command == "quit":
                # 退出程序
                logger.info("Quit main.")
                G.G_RUN.clear()
                logger.info(f"G_RUN status = {G.G_RUN.is_set()}")
                for timer in TaskManager.timers:
                    timer.cancel()

            elif command in consts.KEY_MAPPING:
                # 手柄操作
                control_data = consts.KEY_MAPPING.get(command)
                if isinstance(control_data, str):
                    pro.press_button(control_data, 0)
                    screenshot()
                if isinstance(control_data, types.FunctionType):
                    control_data()
            else:
                global_vars = globals()
                func = global_vars.get(command, "")
                if isinstance(func, types.FunctionType):
                    func()
                else:
                    logger.info(f"{command} command not support!")

        elif isinstance(command, dict):
            logger.info("Received config update message.")
            G.CONFIG = command

        else:
            logger.info(f"{command} command not support!")


def start_command_input(queue):
    t = threading.Thread(target=command_input, args=(queue,), daemon=True)
    t.start()


def worker(input_queue, output_queue):
    G.G_RACE_QUIT_EVENT.set()
    G.G_RUN.set()
    G.output_queue = output_queue

    start_command_input(input_queue)
    while G.G_RUN.is_set():
        if G.G_RACE_RUN_EVENT.is_set():
            event_loop()
        else:
            time.sleep(1)
    logger.info("Woker quit.")


def start_worker():
    p = multiprocessing.Process(target=worker, args=(G.input_queue, G.output_queue))
    p.daemon = True
    p.start()


def output_worker(app, event):
    logger.info("Start output worker.")
    while event.is_set():
        text = G.output_queue.get()
        app.show(text)
    # logger.info("Output worker quit.")


def start_output_worker(app):
    t = threading.Thread(target=output_worker, args=(app, G.G_OUT_WORKER), daemon=True)
    t.start()


def on_closing(app):
    G.G_RUN.clear()
    logger.info(f"G_RUN state {G.G_RUN.is_set()}")
    G.output_queue.put("Quit App.")
    app.destroy()


def init_config():

    parser = argparse.ArgumentParser(description="NS Asphalt9 Tool.")
    parser.add_argument("-c", "--config", type=str, default="settings", help="自定义配置文件")
    args = parser.parse_args()
    return args.config


def main():
    G.G_OUT_WORKER.set()
    config_name = init_config()
    start_worker()
    app = App(G.input_queue, config_name)
    start_output_worker(app)
    app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
    app.mainloop()
    print("App quit quit.")


if __name__ == "__main__":
    main()

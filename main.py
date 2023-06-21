import argparse
import datetime
import json
import shutil
import threading
import time
import traceback
import types

import yaml

from core import consts
from core import globals
from core.controller import Buttons, pro

from core.pages import Page
from core.screenshot import screenshot
from utils.log import logger


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


class TaskManager:
    timers = []
    status = consts.TaskStatus.default
    current_task = ""

    @classmethod
    def task_init(cls):
        if "任务" not in consts.CONFIG:
            return
        for task in consts.CONFIG["任务"]:
            if task["间隔"] > 0:
                timer = cls.task_producer(task["名称"], task["间隔"])
                cls.timers.append(timer)
        cls.task_enter()

    @classmethod
    def task_producer(cls, task, duration, skiped=False):
        if skiped:
            consts.task_queue.put(task)
        else:
            logger.info(f"Start task {task} producer, duration = {duration}min")
            skiped = True
        timer = threading.Timer(
            duration * 60, cls.task_producer, (task, duration), {"skiped": skiped}
        )
        timer.start()
        return timer

    @classmethod
    def task_dispatch(cls, page: Page) -> None:
        if "任务" not in consts.CONFIG:
            return False

        if page.name not in [
            consts.world_series,
            consts.limited_series,
            consts.trial_series,
            consts.carhunt,
            consts.card_pack,
        ]:
            return False

        if consts.task_queue.empty():
            if cls.status == consts.TaskStatus.done:
                cls.task_enter()
                cls.status = consts.TaskStatus.default
                return True
        else:
            task = consts.task_queue.get()
            logger.info(f"Get {task} task from queue.")
            cls.status = consts.TaskStatus.start
            cls.current_task = task
            cls.task_enter(task)
            return True

    @classmethod
    def task_enter(cls, task: str = "") -> None:
        if not task:
            task = CONFIG["task"]
        logger.info(f"Start process {task} task.")
        if task == consts.TaskName.world_series:
            enter_series()
        if task == consts.TaskName.other_series:
            enter_series(task)
        if task == consts.TaskName.car_hunt:
            enter_carhunt()
        if task == consts.TaskName.free_pack:
            free_pack()

    @classmethod
    def set_done(cls) -> None:
        if cls.status == consts.TaskStatus.start:
            cls.status = consts.TaskStatus.done
            cls.current_task = ""


def event_loop():
    TaskManager.task_init()

    while consts.G_RACE_RUN_EVENT.is_set() and consts.G_RUN.is_set():
        try:
            page = ocr_screen()
            if page.division:
                consts.DIVISION = page.division
            if page.mode:
                consts.MODE = page.mode
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

    consts.G_RACE_QUIT_EVENT.set()


def command_input():
    while consts.G_RUN.is_set():
        command = input("Please input command \n")

        if command == "stop":
            # 停止挂机
            if consts.G_RACE_RUN_EVENT.is_set():
                consts.G_RACE_RUN_EVENT.clear()
                logger.info("Stop event loop.")
                consts.G_RACE_QUIT_EVENT.wait()
                logger.info("Event loop stoped.")
            else:
                logger.info("Event loop not running.")

        elif command == "run":
            # 开始挂机
            if consts.G_RACE_RUN_EVENT.is_set():
                logger.info("Event loop is running.")
            else:
                consts.G_RACE_RUN_EVENT.set()
                consts.G_RACE_QUIT_EVENT.clear()
                logger.info("Start run event loop.")

        elif command == "quit":
            # 退出程序
            logger.info("Quit main.")
            consts.G_RUN.clear()
            for timer in TaskManager.timers:
                timer.cancel()

        elif command in consts.KEY_MAPPING:
            # 手柄操作
            control_data = consts.KEY_MAPPING.get(command)
            if isinstance(control_data, str):
                pro.press_buttons(control_data)
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


def start_command_input():
    t = threading.Thread(target=command_input, args=())
    t.start()


def init_config():
    global CONFIG
    parser = argparse.ArgumentParser(description="NS Asphalt9 Tool.")
    parser.add_argument("-c", "--config", type=str, help="自定义配置文件")
    parser.add_argument("-t", "--task", type=int, default=1, help="1 多人一 2 多人二 3 寻车")

    args = parser.parse_args()

    with open("default.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if args.config:
        with open(args.config) as f:
            custom_config = yaml.load(f, Loader=yaml.FullLoader)
        config.update(custom_config)
    mode_mapping = {1: "world_series", 2: "other_series", 3: "car_hunt"}
    config.update({"task": mode_mapping.get(args.task)})
    logger.info(f"config = {json.dumps(config, indent=2, ensure_ascii=False)}")
    CONFIG = config


def main():
    consts.G_RACE_QUIT_EVENT.set()
    consts.G_RUN.set()

    init_config()

    start_command_input()

    while consts.G_RUN.is_set():
        if consts.G_RACE_RUN_EVENT.is_set():
            event_loop()
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()

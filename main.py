import argparse
import datetime
import re
import shutil
import threading
import time
import traceback
import yaml
import types
import json
import queue


import consts
from ocr import Page, ocr
from screenshot import screenshot
from utils.controller import Buttons, pro
from utils.log import logger
from utils.decorator import retry


task_queue = queue.Queue()


CONFIG = None

FINISHED_COUNT = 0

# 程序运行
G_RUN = threading.Event()

# 退出循环事件
G_RACE_RUN_EVENT = threading.Event()
G_RACE_QUIT_EVENT = threading.Event()

# 是否活跃状态
NO_OPERATION_COUNT = 0

# 游戏模式
MODE = ""

# 段位
DIVISION = ""

# 选车次数
SELECT_COUNT = 0

# 键盘与手柄映射
KEY_MAPPING = {
    "6": "MINUS",
    "7": "PLUS",
    "[": "CAPTURE",
    "]": "HOME",
    "i": "X",
    "j": "Y",
    "l": "A",
    "k": "B",
    "s": "DPAD_DOWN",
    "w": "DPAD_UP",
    "a": "DPAD_LEFT",
    "d": "DPAD_RIGHT",
    "c": screenshot,
}


def has_text(identity, page_text):
    """page_text中是否包含identity"""
    if re.findall(identity, page_text):
        return True
    return False


def ocr_screen():
    """截图并识别"""
    screenshot()
    page = ocr()
    return page


def enter_game():
    """进入游戏"""
    buttons = [
        Buttons.B,
        Buttons.DPAD_UP,
        Buttons.DPAD_LEFT,
        Buttons.DPAD_LEFT,
        Buttons.A,
        Buttons.A,
    ]
    pro.press_group(buttons, 0.5)


@retry(max_attempts=3)
def reset_to_career():
    """重置到生涯"""
    pro.press_group([Buttons.B] * 5, 2)
    pro.press_group([Buttons.DPAD_DOWN] * 5, 0.5)
    pro.press_group([Buttons.DPAD_RIGHT] * 7, 0.5)
    for _ in range(2):
        pro.press_group([Buttons.A], 3)
        page = ocr_screen()
        if page.career:
            pro.press_group([Buttons.B], 2)
            break
    else:
        raise Exception(f"Failed to access career, current page = {page.name}")


@retry(max_attempts=3)
def enter_series(mode="world_series"):
    """进入多人赛事"""
    reset_to_career()
    pro.press_group([Buttons.ZL] * 4, 0.5)
    if mode != "world_series":
        pro.press_group([Buttons.DPAD_DOWN], 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A], 2)
    page = ocr_screen()
    if page.name in [Page.world_series, Page.trial_series, Page.limited_series]:
        pass
    else:
        raise Exception(f"Failed to access {mode}, current page = {page.name}")


@retry(max_attempts=3)
def enter_carhunt():
    """进入寻车"""
    global CONFIG
    reset_to_career()
    pro.press_group([Buttons.ZL] * 5, 0.5)
    pro.press_group([Buttons.A], 2)
    # page = ocr_screen()
    # if has_text("TO CLAIM", page.text):
    #     pro.press_a()
    # time.sleep(3)
    # pro.press_group([Buttons.DPAD_RIGHT] * 1, 0.5)
    # pro.press_a(2)
    # pro.press_group([Buttons.ZL] * 1, 0.5)
    pro.press_group([Buttons.ZR] * CONFIG["寻车"]["位置"], 0.5)
    time.sleep(2)
    page = ocr_screen()
    if has_text("CAR HUNT", page.text):
        pro.press_a()
    else:
        pro.press_group([Buttons.ZL] * 12, 0)
        for i in range(20):
            pro.press_group([Buttons.ZR], 1)
            page = ocr_screen()
            if has_text("CAR HUNT", page.text):
                CONFIG["寻车"]["位置"] = i + 1
                pro.press_a()
                break
        else:
            raise Exception(f"Failed to access carhunt, current page = {page.name}")


@retry(max_attempts=3)
def free_pack():
    """领卡"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.5)
    pro.press_group([Buttons.DPAD_LEFT] * 8, 0.5)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP], 0.5)
    pro.press_group([Buttons.A] * 2, 5)
    page = ocr_screen()
    if has_text("CLASSIC PACK.*POSSIBLE CONTENT", page.text):
        pro.press_group([Buttons.A] * 3, 3)
        pro.press_group([Buttons.B], 0.5)
        TaskManager.set_done()
    else:
        raise Exception(f"Failed to access carhunt, current page = {page.name}")


def world_series_reset():
    division = DIVISION
    if not division:
        division = "BRONZE"
    config = CONFIG["多人一"][division]
    level = config["车库等级"]
    left_count_mapping = {"BRONZE": 4, "SILVER": 3, "GOLD": 2, "PLATINUM": 1}
    pro.press_group([Buttons.DPAD_UP] * 4, 0)
    pro.press_group([Buttons.DPAD_RIGHT] * 6, 0)
    pro.press_group([Buttons.DPAD_LEFT] * 1, 0)
    pro.press_group([Buttons.DPAD_DOWN] * 1, 0)
    pro.press_group([Buttons.DPAD_LEFT] * left_count_mapping.get(level), 0)
    time.sleep(1)
    pro.press_a(2)


def default_reset():
    pass


def other_series_reset():
    pro.press_button(Buttons.ZL, 0)


def carhunt_reset():
    pro.press_button(Buttons.ZR, 0)
    pro.press_button(Buttons.ZL, 1)


def default_positions():
    positions = []
    for row in [1, 2]:
        for col in [1, 2, 3]:
            positions.append({"row": row, "col": col})
    return positions


def world_series_positions():
    division = DIVISION
    if not division:
        division = "BRONZE"
    config = CONFIG["多人一"][division]
    return config["车库位置"]


def other_series_position():
    return CONFIG["多人二"]["车库位置"]


def carhunt_position():
    return CONFIG["寻车"]["车库位置"]


def move_to_position(positions):
    global SELECT_COUNT
    if not positions:
        return
    if SELECT_COUNT >= len(positions):
        SELECT_COUNT = 0
    position = positions[SELECT_COUNT]
    for _ in range(position["row"] - 1):
        pro.press_button(Buttons.DPAD_DOWN, 0)
    for _ in range(position["col"] - 1):
        pro.press_button(Buttons.DPAD_RIGHT, 0)


def get_race_config():
    task = consts.ModeTaskMapping.get(MODE, CONFIG["task"])
    if task == consts.TaskName.other_series:
        return other_series_position(), other_series_reset
    elif task == consts.TaskName.car_hunt:
        return carhunt_position(), carhunt_reset
    elif task == consts.TaskName.world_series:
        return world_series_positions(), world_series_reset
    else:
        return default_positions(), default_reset


def select_car():
    global SELECT_COUNT
    global DIVISION
    # 选车
    while G_RUN.is_set():
        positions, reset = get_race_config()
        reset()
        move_to_position(positions)

        time.sleep(2)

        pro.press_group([Buttons.A], 2)

        page = ocr_screen()

        # 如果没有进到车辆详情页面, router到默认任务
        if page.name != Page.car_info:
            TaskManager.task_enter()
            return

        pro.press_group([Buttons.A], 2)

        page = ocr_screen()

        if page.name in [
            Page.loading_race,
            Page.searching,
            Page.racing,
            Page.loading_carhunt,
        ]:
            break
        elif page.name == Page.tickets:
            pro.press_button(Buttons.DPAD_DOWN, 2)
            pro.press_a(2)
            pro.press_b(2)
            pro.press_a(2)
        else:
            if page.name == Page.car_info and has_text(
                "BRONZE|SILVER|GOLD|PLATINUM", page.text
            ):
                DIVISION = ""
            for i in range(2):
                pro.press_b()
                page = ocr_screen()
                if page.name == Page.select_car:
                    break
            SELECT_COUNT += 1
            continue
    process_race()
    TaskManager.set_done()


def process_race(race_mode=0):
    global FINISHED_COUNT
    for i in range(60):
        progress = 0
        page = ocr_screen()
        if page.data and "progress" in page.data:
            progress = page.data["progress"] if page.data["progress"] else 0
        if race_mode == 1:
            if progress > 0 and progress < 22:
                pro.press_buttons(Buttons.Y)
                time.sleep(0.4)
                pro.press_buttons(Buttons.Y)
                pro.press_buttons(Buttons.DPAD_LEFT)
            if progress >= 22:
                pro.press_buttons(Buttons.ZL, 23)
                for _ in range(10):
                    pro.press_buttons(Buttons.Y)
                    pro.press_buttons(Buttons.Y)
            time.sleep(1)
        elif race_mode == 2:
            if progress > 0:
                start = time.perf_counter()
                delta = progress * 0.55 + 4.5
                while G_RUN.is_set():
                    end = time.perf_counter()
                    elapsed = end - start + delta
                    logger.info(f"elapsed = {elapsed}")
                    if elapsed >= 14 and elapsed <= 15.5:
                        pro.press_buttons(Buttons.B, 3)
                    elif elapsed >= 17 and elapsed <= 18.5:
                        pro.press_buttons(Buttons.DPAD_LEFT)
                        pro.press_buttons(Buttons.B, 3)
                    elif elapsed >= 21 and elapsed <= 22:
                        pro.press_buttons(Buttons.Y)
                        pro.press_buttons(Buttons.Y)
                    elif elapsed > 22 and elapsed < 24:
                        pro.press_buttons(Buttons.DPAD_LEFT)
                    elif elapsed >= 43 and elapsed < 48:
                        pro.press_buttons(Buttons.B, 5)
                        pro.press_buttons(Buttons.Y)
                        pro.press_buttons(Buttons.Y)
                    elif elapsed > 60:
                        break
                    elif elapsed > 24 and elapsed < 43 or elapsed < 10:
                        pro.press_button(Buttons.Y, 0.7)
                        pro.press_button(Buttons.Y, 0)
                        time.sleep(3)
                    else:
                        time.sleep(0.5)
        elif MODE == "CAR_HUNT_APEX_AP0":
            if progress > 0:
                start = time.perf_counter()
                delta = progress * 0.55 + 4.5
                while G_RUN.is_set():
                    end = time.perf_counter()
                    elapsed = end - start + delta
                    logger.info(f"elapsed = {elapsed}")
                    if elapsed < 5 and elapsed >= 3.5:
                        pro.press_button(Buttons.DPAD_LEFT, 0)
                    elif elapsed >= 7.5 and elapsed <= 9:
                        pro.press_buttons(Buttons.DPAD_RIGHT, 3)
                    elif elapsed >= 38 and elapsed < 41:
                        pro.press_buttons(Buttons.B, 4)
                        pro.press_buttons(Buttons.Y)
                        pro.press_buttons(Buttons.Y)
                    elif elapsed > 60:
                        break
                    elif elapsed > 9 and elapsed < 35:
                        pro.press_button(Buttons.Y, 0.7)
                        pro.press_button(Buttons.Y, 0)
                        time.sleep(2)
                    else:
                        time.sleep(0.5)

        else:
            pro.press_button(Buttons.Y, 0.7)
            pro.press_button(Buttons.Y, 0)

        if page.name in [Page.race_score, Page.race_results, Page.race_reward]:
            break

    FINISHED_COUNT += 1
    logger.info(f"Already finished {FINISHED_COUNT} times loop count = {i}.")


def connect_controller():
    """连接手柄"""
    pro.press_buttons([Buttons.L, Buttons.R], down=1)
    time.sleep(1)
    pro.press_buttons([Buttons.A], down=0.5)


def demoted():
    """降级"""
    global DIVISION
    DIVISION = ""
    pro.press_button(Buttons.B, 3)


def process_screen(page):
    """根据显示内容执行动作"""

    global NO_OPERATION_COUNT
    pages_action = [
        {
            "pages": [Page.loading_race],
            "action": process_race,
        },
        {
            "pages": [Page.connect_controller],
            "action": connect_controller,
        },
        {
            "pages": [Page.connected_controller],
            "action": enter_game,
        },
        {
            "pages": [Page.multi_player],
            "action": enter_series,
            "args": (),
        },
        {
            "pages": [Page.daily_events],
            "action": enter_carhunt,
            "args": (),
        },
        {
            "pages": [
                Page.world_series,
                Page.limited_series,
                Page.trial_series,
                Page.carhunt,
            ],
            "action": pro.press_button,
            "args": (Buttons.A, 3),
        },
        {
            "pages": [Page.select_car],
            "action": select_car,
            "args": (),
        },
        {
            "pages": [Page.car_info],
            "action": pro.press_button,
            "args": (Buttons.A, 3),
        },
        {
            "pages": [Page.searching],
            "action": pro.press_button,
            "args": (Buttons.Y, 3),
        },
        {
            "pages": [Page.demoted],
            "action": demoted,
            "args": (),
        },
        {
            "pages": [
                Page.disconnected,
                Page.no_connection,
                Page.club_reward,
                Page.vip_reward,
                Page.server_error,
                Page.club,
                Page.no_opponents,
            ],
            "action": pro.press_button,
            "args": (Buttons.B,),
        },
        {
            "pages": [
                Page.race_score,
                Page.race_reward,
                Page.race_results,
                Page.milestone_reward,
                Page.connect_error,
                Page.star_up,
                Page.game_menu,
            ],
            "action": pro.press_button,
            "args": (Buttons.A,),
        },
        {
            "pages": [Page.offline_mode],
            "action": pro.press_group,
            "args": ([Buttons.DPAD_LEFT, Buttons.B], 1),
        },
        {
            "pages": [Page.system_error, Page.switch_home],
            "action": pro.press_group,
            "args": ([Buttons.A] * 3, 3),
        },
        {
            "pages": [Page.card_pack],
            "action": pro.press_group,
            "args": ([Buttons.B] * 2, 3),
        },
    ]

    for p in pages_action:
        if page.name in p["pages"]:
            logger.info(f"Match page {page.name}")
            action = p["action"]
            args = p["args"] if "args" in p else ()
            action(*args)
            break
    else:
        logger.info("Match none page.")
        NO_OPERATION_COUNT += 1
        if NO_OPERATION_COUNT > 30:
            logger.info("Keep alive press button y")
            pro.press_buttons(Buttons.Y)
            NO_OPERATION_COUNT = 0


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
        if "任务" not in CONFIG:
            return
        for task in CONFIG["任务"]:
            if task["间隔"] > 0:
                timer = cls.task_producer(task["名称"], task["间隔"])
                cls.timers.append(timer)
        cls.task_enter()

    @classmethod
    def task_producer(cls, task, duration, skiped=False):
        if skiped:
            task_queue.put(task)
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
        if "任务" not in CONFIG:
            return False

        if page.name not in [
            Page.world_series,
            Page.limited_series,
            Page.trial_series,
            Page.carhunt,
            Page.card_pack,
        ]:
            return False

        if task_queue.empty():
            if cls.status == consts.TaskStatus.done:
                cls.task_enter()
                cls.status = consts.TaskStatus.default
                return True
        else:
            task = task_queue.get()
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
    global G_RACE_QUIT_EVENT
    global DIVISION
    global MODE

    TaskManager.task_init()

    while G_RACE_RUN_EVENT.is_set() and G_RUN.is_set():
        try:
            page = ocr_screen()
            if page.division:
                DIVISION = page.division
            if page.mode:
                MODE = page.mode
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

    G_RACE_QUIT_EVENT.set()


def command_input():
    global G_RUN
    global G_RACE_RUN_EVENT
    global G_RACE_QUIT_EVENT

    while G_RUN.is_set():
        command = input("Please input command \n")

        if command == "stop":
            # 停止挂机
            if G_RACE_RUN_EVENT.is_set():
                G_RACE_RUN_EVENT.clear()
                logger.info("Stop event loop.")
                G_RACE_QUIT_EVENT.wait()
                logger.info("Event loop stoped.")
            else:
                logger.info("Event loop not running.")

        elif command == "run":
            # 开始挂机
            if G_RACE_RUN_EVENT.is_set():
                logger.info("Event loop is running.")
            else:
                G_RACE_RUN_EVENT.set()
                G_RACE_QUIT_EVENT.clear()
                logger.info("Start run event loop.")

        elif command == "quit":
            # 退出程序
            logger.info("Quit main.")
            G_RUN.clear()
            for timer in TaskManager.timers:
                timer.cancel()

        elif command in KEY_MAPPING:
            # 手柄操作
            control_data = KEY_MAPPING.get(command)
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
    global G_RACE_RUN_EVENT
    global G_RACE_QUIT_EVENT

    G_RACE_QUIT_EVENT.set()
    G_RUN.set()

    init_config()

    start_command_input()

    while G_RUN.is_set():
        if G_RACE_RUN_EVENT.is_set():
            event_loop()
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()

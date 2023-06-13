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


from ocr import Page, ocr
from screenshot import screenshot
from utils.controller import Buttons, pro
from utils.log import logger


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


def wait_for(text, timeout=10):
    """等待屏幕出现text"""
    count = 0
    logger.info(f"Wait for text = {text}")
    while True:
        page = ocr_screen()
        if has_text(text, page.text):
            return page
        count += 1
        time.sleep(1)
        if count > timeout:
            raise Exception(f"Wait for text = {text} timeout!")


def wait_for_page(page_name, timeout=10):
    """等待屏幕出现text"""
    count = 0
    logger.info(f"Wait for page = {page_name}")
    while True:
        page = ocr_screen()
        if page.name == page_name:
            return page
        count += 1
        time.sleep(1)
        if count > timeout:
            raise Exception(f"Wait for page = {page_name} timeout!")


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


def enter_series(upcount=None):
    """进入多人赛事"""
    pro.press_group([Buttons.B] * 5, 2)
    pro.press_group([Buttons.DPAD_DOWN] * 5, 0.5)
    pro.press_group([Buttons.DPAD_RIGHT] * 7, 0.5)
    pro.press_group([Buttons.A] * 1, 0.5)
    pro.press_group([Buttons.DPAD_LEFT] * 4, 0.5)
    pro.press_group([Buttons.A] * 1, 0.5)
    if upcount is None:
        upcount = 2 if MODE == "WORLD SERIES" else 1
    pro.press_group([Buttons.DPAD_UP] * upcount, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A] * 1, 0.5)


def enter_carhunt():
    """进入寻车"""
    pro.press_group([Buttons.B] * 5, 2)
    pro.press_group([Buttons.DPAD_DOWN] * 5, 0.5)
    pro.press_group([Buttons.DPAD_RIGHT] * 7, 0.5)
    pro.press_group([Buttons.A] * 1, 0.5)
    pro.press_group([Buttons.DPAD_LEFT] * 5, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A] * 2, 0.5)
    time.sleep(2)
    page = ocr_screen()
    if has_text("TO CLAIM", page.text):
        pro.press_a()
    pro.press_group([Buttons.DPAD_RIGHT] * CONFIG["寻车"]["位置"], 0.5)
    time.sleep(2)
    pro.press_a()
    page = ocr_screen()
    if page.name == Page.carhunt:
        pro.press_a()
    else:
        pro.press_group([Buttons.DPAD_RIGHT] * 12, 0)
        for _ in range(12):
            pro.press_button(Buttons.DPAD_LEFT, 1)
            page = ocr_screen()
            if page.name == Page.carhunt:
                pro.press_a()
                break
        else:
            raise Exception("Can`t find car hunt page.")


def free_pack():
    """领卡"""
    global FINISHED_COUNT
    page = ocr_screen()
    if has_text("FREE PACK", page.text):
        pro.press_group([Buttons.DPAD_UP] * 5, 0.5)
        pro.press_group([Buttons.DPAD_LEFT] * 7, 0.5)
        pro.press_group([Buttons.DPAD_RIGHT] * 3, 0.5)
        pro.press_a(4)
        pro.press_group([Buttons.A] * 3, 2)
        pro.press_group([Buttons.B] * 3, 0.5)
    FINISHED_COUNT += 1


def play_game(select_car=1):
    """点击play并等待进入到选车界面"""
    pro.press_a(0.1)
    if select_car:
        for i in range(20):
            time.sleep(1)
            page = ocr_screen()
            if page.name == Page.select_car:
                break


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
    pro.press_button(Buttons.ZL, 0)


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


def get_series_config():
    if MODE in ["LIMITED SERIES", "TRIAL SERIES"]:
        return other_series_position(), other_series_reset
    elif MODE == "CAR HUNT":
        return carhunt_position(), carhunt_reset
    elif MODE == "WORLD SERIES":
        return world_series_positions(), world_series_reset
    else:
        return default_positions(), default_reset


def select_car():
    global SELECT_COUNT
    global DIVISION
    # 选车
    while G_RUN.is_set():
        positions, reset = get_series_config()
        reset()
        if SELECT_COUNT >= len(positions):
            SELECT_COUNT = 0
        position = positions[SELECT_COUNT]

        for i in range(position["row"] - 1):
            pro.press_button(Buttons.DPAD_DOWN, 0)

        for i in range(position["col"] - 1):
            pro.press_button(Buttons.DPAD_RIGHT, 0)

        time.sleep(2)

        pro.press_group([Buttons.A] * 2, 2)

        page = ocr_screen()

        if page.name in [Page.loading_race, Page.searching, Page.racing]:
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
    world_series = "world_series"
    other_series = "other_series"
    car_hunt = "car_hunt"
    free_pack = "free_pack"

    last_mode = None

    def __init__(self) -> None:
        self.task_init()

    def task_init(self):
        if "任务" not in CONFIG:
            return
        for task in CONFIG["任务"]:
            if task["间隔"] > 0:
                self.task_producer(task["名称"], task["间隔"])

    def task_producer(self, task, duration, skiped=False):
        if skiped:
            task_queue.put(task)
        else:
            logger.info(f"Start task {task} producer, duration = {duration}min")
            skiped = True
        timer = threading.Timer(
            duration * 60, self.task_producer, (task, duration), {"skiped": skiped}
        )
        timer.start()

    def task_dispatch(self, page):
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
            if self.last_mode:
                self.task_enter(mode_name=self.last_mode)
                self.last_mode = ""
                return True
        else:
            self.last_mode = MODE
            task = task_queue.get()
            self.task_enter(task_name=task)
            return True

    def task_enter(self, task_name="", mode_name=""):
        mode_mapping = {
            "WORLD SERIES": "world_series",
            "LIMITED SERIES": "other_series",
            "TRIAL SERIES": "other_series",
            "CAR HUNT": "car_hunt",
        }
        if mode_name:
            task_name = mode_mapping.get(mode_name)
        if task_name == "world_series":
            enter_series(upcount=2)
        if task_name == "other_series":
            enter_series(upcount=1)
        if task_name == "car_hunt":
            enter_carhunt()
        if task_name == "free_pack":
            free_pack()


manager = TaskManager()


def event_loop():
    global G_RACE_QUIT_EVENT
    global DIVISION
    global MODE

    while G_RACE_RUN_EVENT.is_set() and G_RUN.is_set():
        try:
            page = ocr_screen()
            if page.division:
                DIVISION = page.division
            if page.mode:
                MODE = page.mode
            dispatched = manager.task_dispatch(page)
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

        elif command in KEY_MAPPING:
            # 手柄操作
            control_data = KEY_MAPPING.get(command)
            if isinstance(control_data, str):
                pro.press_buttons(control_data)
                screenshot()
            if isinstance(control_data, types.FunctionType):
                control_data()

        else:
            logger.info(f"{command} command not support!")


def start_command_input():
    t = threading.Thread(target=command_input, args=())
    t.start()


def init_config():
    global CONFIG
    parser = argparse.ArgumentParser(description="NS Asphalt9 Tool.")
    parser.add_argument("-c", "--config", type=str, help="自定义配置文件")

    args = parser.parse_args()

    with open("default.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if args.config:
        with open(args.config) as f:
            custom_config = yaml.load(f, Loader=yaml.FullLoader)
        config.update(custom_config)
    logger.info(f"config = {json.dumps(config, indent=2, ensure_ascii=True)}")
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

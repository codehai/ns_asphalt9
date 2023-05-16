import argparse
import datetime
import re
import shutil
import threading
import time
import traceback
import yaml

from ocr import Page, ocr
from screenshot import screenshot
from utils.controller import Buttons, pro
from utils.log import logger


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


def enter_series():
    """进入多人赛事"""
    pro.press_group([Buttons.B] * 5, 0.5)
    pro.press_group([Buttons.DPAD_DOWN] * 5, 0.5)
    pro.press_group([Buttons.DPAD_LEFT] * 5, 0.5)
    pro.press_group([Buttons.DPAD_RIGHT] * 3, 0.5)
    pro.press_group([Buttons.DPAD_UP] * 2, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A] * 1, 0.5)


def enter_carhunt():
    """进入寻车"""
    pro.press_group([Buttons.B] * 5, 0.5)
    pro.press_group([Buttons.DPAD_DOWN] * 5, 0.5)
    pro.press_group([Buttons.DPAD_LEFT] * 5, 0.5)
    pro.press_group([Buttons.DPAD_RIGHT] * 2, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A] * 1, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.DPAD_RIGHT] * 5, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A] * 2, 0.5)


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


def limited_series_reset():
    pro.press_button(Buttons.ZL, 0)


def world_series_positions():
    division = DIVISION
    if not division:
        division = "BRONZE"
    config = CONFIG["多人一"][division]
    return config["车库位置"]


def limited_series_position():
    return CONFIG["多人二"]["车库位置"]


def get_series_config():
    if MODE == "WORLD SERIES":
        return world_series_positions(), world_series_reset
    elif MODE == "LIMITED SERIES":
        return limited_series_position(), limited_series_reset
    else:
        raise Exception("Not support mode in series_select.")


def select_car():
    global SELECT_COUNT
    positions, reset = get_series_config()
    # 选车
    while True:
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
        elif page.name in [Page.car_info]:
            for i in range(2):
                pro.press_b()
                page = ocr_screen()
                if page.name == Page.select_car:
                    break
            SELECT_COUNT += 1
            continue
        else:
            raise Exception("Not support page in world_series_select.")


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
                while True:
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
        else:
            pro.press_button(Buttons.Y, 0.7)
            pro.press_button(Buttons.Y, 0)

        if page.name in [Page.race_score, Page.race_results]:
            break

    FINISHED_COUNT += 1
    logger.info(f"Already finished {FINISHED_COUNT} times loop count = {i}.")


def car_hunt(race_mode=0, row=2, column=5):
    """寻车"""
    logger.info("Start process car hunt.")
    pro.press_a(3)
    logger.info("Wait for select car")
    wait_for("CAR SELECTION")
    logger.info("Start select car")
    select_car(row, column, confirm=0)
    logger.info("Start confirm car")
    pro.press_a(3)
    logger.info("Wait for Play button")
    wait_for("PLAY", 30)
    logger.info("Press play button")
    pro.press_a(3)
    logger.info("OCR screen")
    page = ocr_screen()
    if page.name == Page.tickets:
        pro.press_button(Buttons.DPAD_DOWN, 2)
        pro.press_a(2)
        pro.press_b(2)
        pro.press_a(2)
    logger.info("Start process race")
    process_race(race_mode)
    logger.info("Finished car hunt")


def connect_controller():
    """连接手柄"""
    pro.press_buttons([Buttons.L, Buttons.R], down=1)
    time.sleep(1)
    pro.press_buttons([Buttons.A], down=0.5)


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
            "pages": [Page.multi_player, Page.series, Page.limited_series],
            "action": pro.press_button,
            "args": (Buttons.A, 3),
        },
        {
            "pages": [Page.trial_series],
            "action": pro.press_group,
            "args": ([Buttons.A, Buttons.A], 3),
        },
        {
            "pages": [Page.carhunt],
            "action": car_hunt,
            "args": (2,),
        },
        {
            "pages": [Page.legendary_hunt],
            "action": car_hunt,
            "args": (0, 1, 4),
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
            "pages": [
                Page.demoted,
                Page.disconnected,
                Page.no_connection,
                Page.club_reward,
                Page.vip_reward,
                Page.server_error,
                Page.club,
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
            "pages": [Page.system_error],
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


def event_loop():
    global G_RACE_QUIT_EVENT
    global G_RACE_RUN_EVENT
    global MODE
    global DIVISION

    while G_RACE_RUN_EVENT.is_set() and G_RUN.is_set():
        try:
            page = ocr_screen()
            if page.division:
                DIVISION = page.division
            if page.mode:
                MODE = page.mode
            process_screen(page)
            time.sleep(3)

        except Exception as err:
            filename = capture()
            logger.error(
                f"Caught exception, err = {err}, traceback = {traceback.format_exc()}, \
                  page dict = {page.dict}, filename = {filename}"
            )
            # 出错重新进多人
            # enter_series()

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
            pro.press_buttons(control_data)
            screenshot()
        else:
            logger.info(f"{command} command not support!")


def start_command_input():
    t = threading.Thread(target=command_input, args=())
    t.start()


def init_config():
    global CONFIG
    parser = argparse.ArgumentParser(description="NS Asphalt9 Tool.")
    parser.add_argument("-c", action="store_true", help="使用自定义配置")

    args = parser.parse_args()

    with open("default.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if args.c:
        with open("custom.yaml") as f:
            custom_config = yaml.load(f, Loader=yaml.FullLoader)
        config.update(custom_config)
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

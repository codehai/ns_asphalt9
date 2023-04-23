import datetime
import re
import shutil
import time
import threading

import nxbt
from nxbt import Nxbt
from nxbt import Buttons

from ocr import ocr
from screenshot import screenshot
from utils.log import logger

NX = None
CONTROLLER_INDEX = None
FINISHED_COUNT = 0

# 是否初始化车所在位置
INITED_CAR_POSITION = False

# 程序运行
G_RUN = threading.Event()

# 退出循环事件
G_RACE_RUN_EVENT = threading.Event()
G_RACE_QUIT_EVENT = threading.Event()

# 是否活跃状态
G_IS_ALIVE = threading.Event()
G_CLEAR_COUNT = 0

NO_OPERATION_COUNT = 0

# 正序选车
SELECT_CAR_ACTION = [
    Buttons.DPAD_DOWN,
    Buttons.DPAD_RIGHT,
    Buttons.DPAD_UP,
    Buttons.DPAD_RIGHT,
] * 10
# 反序选车
SELECT_CAR_REVERSE_ACTION = [
    Buttons.DPAD_DOWN,
    Buttons.DPAD_LEFT,
    Buttons.DPAD_UP,
    Buttons.DPAD_LEFT,
] * 10
SELECT_REVERSE = [
    Buttons.DPAD_UP,
    Buttons.DPAD_RIGHT,
    Buttons.DPAD_DOWN,
    Buttons.DPAD_RIGHT,
] * 10
# 选车次数
SELECT_COUNT = -1
# 最多切换车次数(起始值0)
MAX_SELECT_COUNT = 5

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


class BaseNxbt(Nxbt):
    def __init__(self) -> None:
        super().__init__()

    def press_buttons(self, controller_index, buttons, down=0.1, up=0.1, block=True):
        global NO_OPERATION_COUNT
        NO_OPERATION_COUNT = 0
        return super().press_buttons(controller_index, buttons, down, up, block)


def init_controller():
    """连接switch"""
    global NX, CONTROLLER_INDEX
    NX = BaseNxbt()
    CONTROLLER_INDEX = NX.create_controller(nxbt.PRO_CONTROLLER)
    NX.wait_for_connection(CONTROLLER_INDEX)
    time.sleep(1)
    logger.info("Connected switch")
    NX.press_buttons(CONTROLLER_INDEX, [Buttons.A])


def press_group(buttons, sleep=1, shot=1):
    for b in buttons:
        logger.info(f"Press button {b}")
        NX.press_buttons(CONTROLLER_INDEX, [b])
        if sleep:
            time.sleep(sleep)
        if shot:
            screenshot()


def press_button(button, sleep=2, shot=1):
    """按下按键"""
    logger.info(f"Press button {button}")
    NX.press_buttons(CONTROLLER_INDEX, [button])
    if sleep > 0:
        time.sleep(sleep)
    if shot:
        screenshot()


def press_a(sleep=3):
    press_button(Buttons.A, sleep)


def press_b(sleep=2):
    press_button(Buttons.B, sleep)


def has_text(identity, page_text):
    """page_text中是否包含identity"""
    if re.findall(identity, page_text):
        return True
    return False


def wait_for(text, timeout=10):
    """等待屏幕出现text"""
    global G_PAGE_DATA
    count = 0
    logger.info(f"Wait for text = {text}")
    while True:
        screen_text = G_PAGE_DATA["text"]
        if has_text(text, screen_text):
            return screen_text
        count += 1
        time.sleep(1)
        if count > timeout:
            raise Exception(f"Wait for text = {text} timeout!")


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
    press_group(buttons, 0.5, 0)


def enter_series():
    """进入多人赛事"""
    press_group([Buttons.B] * 5, 0.5, 0)
    press_group([Buttons.DPAD_DOWN] * 5, 0.5, 0)
    press_group([Buttons.DPAD_LEFT] * 5, 0.5, 0)
    press_group([Buttons.DPAD_RIGHT] * 3, 0.5, 0)
    # TODO 可选进入多人一还是多人二
    press_group([Buttons.DPAD_UP] * 2, 0.5, 0)
    time.sleep(2)
    press_group([Buttons.A] * 1, 0.5, 0)


def play_game(select_car=1):
    """点击play并等待进入到选车界面"""
    global G_PAGE_DATA
    press_a(0.1)
    if select_car:
        for i in range(20):
            time.sleep(1)
            text = G_PAGE_DATA["text"]
            if has_text("CAR SELECTION", text):
                break


def auto_select_car(reverse=False):
    """自动选车"""
    global INITED_CAR_POSITION
    global SELECT_COUNT
    logger.info("Auto select car.")
    # 车库重置到第一辆车
    if reverse and not INITED_CAR_POSITION:
        for i in range(5):
            press_button(Buttons.DPAD_RIGHT, 0.1)
        INITED_CAR_POSITION = True

    # 选车
    if reverse:
        select_action = SELECT_CAR_REVERSE_ACTION
    else:
        select_action = SELECT_CAR_ACTION

    while True:
        logger.info(f"select_count = {SELECT_COUNT}")
        # SELECT_COUNT 判断重置 使用过5辆车
        if SELECT_COUNT >= MAX_SELECT_COUNT:
            actions = SELECT_REVERSE[: SELECT_COUNT + 1]
            actions.reverse()
            for action in actions:
                press_button(action, 0.2)
            time.sleep(2)
            SELECT_COUNT = -1

        # 检查车辆是否可用
        press_a()
        text = wait_for("TOP SPEED|HANDLING")
        if has_text("GET KEY", text):
            press_b()
            wait_for("CAR SELECTION")
            SELECT_COUNT += 1
            press_button(select_action[SELECT_COUNT], 2)
            continue

        # 处理跳到第一辆车的情况, 重置车的位置
        if has_text("EMIRA", text):
            press_b(3)
            wait_for("CAR SELECTION")

            # 重置
            action = Buttons.DPAD_RIGHT if reverse else Buttons.DPAD_LEFT
            for i in range(5):
                press_button(action, 0.2)
            time.sleep(2)

            # 快进select
            for step in range(SELECT_COUNT + 1):
                press_button(select_action[step], 0.2)
            time.sleep(2)
            press_a()

        press_a(5)
        text = G_PAGE_DATA["text"]
        # 点两下a能开始比赛说明车可用
        if has_text("SEARCHING", text):
            return

        for i in range(2):
            if has_text("TOP SPEED|HANDLING", text):
                press_b(3)
            if has_text("CAR SELECTION", text):
                break
            text = G_PAGE_DATA["text"]
            time.sleep(2)

        SELECT_COUNT += 1
        press_button(select_action[SELECT_COUNT], 2)


def select_car(row, column, confirm=1):
    """开始比赛并选择车
    row 第几行
    column 第几列
    row: 1 column: 4 选择第1行第4列那辆车
    """
    logger.info("Start select car.")
    # 车库重置到第一辆车
    for i in range(25):
        press_button(Buttons.DPAD_LEFT, 0, 0)

    for i in range(3):
        press_button(Buttons.DPAD_UP, 0, 0)

    # 选车
    for i in range(row):
        press_button(Buttons.DPAD_DOWN, 0, 0)

    for i in range(column - 1):
        press_button(Buttons.DPAD_RIGHT, 0, 0)

    time.sleep(2)

    if confirm:
        confirm_and_play()


def confirm_and_play():
    # 确认车辆
    logger.info("Confirm car")
    press_a(2)
    # 开始比赛
    logger.info("Start race")
    press_a(3)


def process_race(race_mode=0):
    global FINISHED_COUNT
    global G_PAGE_DATA

    logger.info("Start process race")

    for _ in range(100):
        text = G_PAGE_DATA["text"]
        position = re.findall(r"\d/\d", text)
        position = position[0] if position else ""
        progress = re.findall(r"\d+%", text)
        progress = progress[0] if progress else ""
        logger.info(f"Current position {position}, progress {progress}")

        if has_text("NEXT|RATING|WINNER|YOUR", text):
            break

        if race_mode == 1:
            progress = int(progress.replace("%", ""))
            if progress > 0 and progress < 22:
                NX.press_buttons(CONTROLLER_INDEX, [Buttons.Y])
                time.sleep(0.4)
                NX.press_buttons(CONTROLLER_INDEX, [Buttons.Y])
                NX.press_buttons(CONTROLLER_INDEX, [Buttons.DPAD_LEFT])
            if progress >= 22:
                NX.press_buttons(CONTROLLER_INDEX, [Buttons.ZL], 23)
                for _ in range(10):
                    NX.press_buttons(CONTROLLER_INDEX, [Buttons.Y])
                    NX.press_buttons(CONTROLLER_INDEX, [Buttons.Y])
            time.sleep(1)
        else:
            press_button(Buttons.Y, 0.7, 0)
            press_button(Buttons.Y, 0, 0)
            time.sleep(3)

    FINISHED_COUNT += 1
    logger.info(f"Already finished {FINISHED_COUNT} times.")


def car_hunt():
    """寻车"""
    global G_PAGE_DATA
    race_mode = 0
    if "BOLWELL" in G_PAGE_DATA["text"]:
        race_mode = 1
    logger.info("Start process car hunt.")
    press_a(3)
    wait_for("CAR SELECTION")
    select_car(2, 5, confirm=0)
    press_a(3)
    wait_for("PLAY", 30)
    press_a(3)
    text = G_PAGE_DATA["text"]
    if "TICKETS" in text:
        press_button(Buttons.DPAD_DOWN, 2)
        press_a(2)
        press_b(2)
        press_a(2)
    process_race(race_mode)


def connect_controller():
    """连接手柄"""
    NX.press_buttons(CONTROLLER_INDEX, [Buttons.L, Buttons.R], 1)
    time.sleep(1)
    NX.press_buttons(CONTROLLER_INDEX, [Buttons.A], 0.5)


def process_screen(text):
    """根据显示内容执行动作"""

    page_mapping = {
        "loading_game": {
            "identity": "LOADING RACE",
            "action": process_race,
            "args": (),
        },
        "connect_controller": {
            "identity": "Press.*on the controller",
            "action": connect_controller,
            "args": (),
        },
        "enter_game": {
            "identity": "Controllers",
            "action": enter_game,
            "args": (),
        },
        # "play_game": {
        #     "identity": "WORLD|LIMITED|TRIAL|CLASSIC",
        #     "action": play_game,
        #     "args": (0,),
        # },
        "enter_series": {
            "identity": "WORLD.*(TRIAL)",
            "action": enter_series,
            "args": (),
        },
        "play_trial": {
            "identity": "TRIAL",
            "action": play_game,
            "args": (0,),
        },
        "play_classic": {
            "identity": "CLASSIC|WORLD SERIES",
            "action": play_game,
            "args": (1,),
        },
        "car_hunt": {
            "identity": "CAR HUNT.*PORSCHE 718 CAYMAN GT4|CAR HUNT.*BOLWELL",
            "action": car_hunt,
            "args": (),
        },
        "select_cat": {
            "identity": "CAR SELECTION",
            "action": select_car,
            "args": (1, 4),
        },
        # "auto_select_cat": {
        #     "identity": "CAR SELECTION",
        #     "action": auto_select_car,
        #     "args": (1,),
        # },
        "confirm_car": {
            "identity": "TOP SPEED|HANDLING|NITRO",
            "action": press_button,
            "args": (Buttons.A, 3),
        },
        "search_game": {
            "identity": "SEARCHING",
            "action": press_button,
            "args": (Buttons.Y, 3),
        },
        "back": {
            "identity": "DEMOTED|DISCONNECTED|NO CONNECTION|YOUR CLUB ACHIEVED|CONGRATULATIONS.*IMPROVE|TIER",
            "action": press_button,
            "args": (Buttons.B,),
        },
        "next_page": {
            "identity": "NEXT|RATING|WINNER|YOUR|CONGRATULATIONS|CONNECTION ERROR|STAR UP",
            "not_in": "YOUR CAR",
            "action": press_button,
            "args": (Buttons.A,),
        },
        "offline_mode_no": {
            "identity": "OFFLINE MODE",
            "action": press_group,
            "args": ([Buttons.DPAD_LEFT, Buttons.B], 1, 1),
        },
        "system_error": {
            "identity": "software.*closed",
            "action": press_group,
            "args": ([Buttons.A] * 3, 1, 1),
        },
    }
    match_page = []
    for page in page_mapping:
        if has_text(page_mapping[page]["identity"], text):
            if "not_in" in page_mapping[page]:
                if not has_text(page_mapping[page]["not_in"], text):
                    logger.info(f"match identity: {page_mapping[page]['identity']}")
                    match_page.append(page)
            else:
                logger.info(f"match identity: {page_mapping[page]['identity']}")
                match_page.append(page)
    logger.info(f"match results: {match_page}")
    if len(match_page) >= 1:
        page_data = page_mapping[match_page[0]]
        action = page_data["action"]
        args = page_data["args"]
        action(*args)
    else:
        logger.info("Match none page. Sleep 3 seconds and try again.")
        time.sleep(3)


def capture():
    filename = "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
    shutil.copy("./images/output.jpg", f"./images/{filename}")
    return filename


def event_loop():
    global G_RACE_QUIT_EVENT
    global G_RACE_RUN_EVENT
    global G_PAGE_DATA

    while G_RACE_RUN_EVENT.is_set() and G_RUN.is_set():
        try:
            text = G_PAGE_DATA["text"]
            has_words = re.findall("\w", text)
            if has_words:
                process_screen(text)
            else:
                logger.info(f"Detect nothing, continue.")
                time.sleep(2)
        except Exception as err:
            filename = capture()
            logger.error(
                f"Caught exception, err = {err}, page text = {text}, filename = {filename}"
            )
            # 出错重新进多人
            # enter_series()

    G_RACE_QUIT_EVENT.set()


def start_event_loop():
    t = threading.Thread(target=event_loop, args=())
    t.start()


def keep_alive():
    """每60秒检测一次是否是活跃状态"""
    global NO_OPERATION_COUNT
    while G_RUN.is_set():
        NO_OPERATION_COUNT += 1
        time.sleep(1)
        if NO_OPERATION_COUNT > 60:
            # 如果退出了event loop并且没有指令输入， 按一下y键防止断开手柄连接
            logger.info("Keep alive press button y")
            NX.press_buttons(CONTROLLER_INDEX, [Buttons.Y])
            NO_OPERATION_COUNT = 0


def start_keep_alive():
    t = threading.Thread(target=keep_alive, args=())
    t.start()


def command_input():
    global G_RUN
    global G_RACE_RUN_EVENT
    global G_RACE_QUIT_EVENT
    global G_IS_ALIVE
    global G_CLEAR_COUNT

    while G_RUN.is_set():
        command = input("Please input command \n")
        G_CLEAR_COUNT = 0
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
                start_event_loop()

        elif command == "quit":
            # 退出程序
            logger.info("Quit main.")
            G_RUN.clear()

        elif command in KEY_MAPPING:
            # 手柄操作
            if G_RACE_RUN_EVENT.is_set():
                logger.info("Please stop event loop first.")
            else:
                control_data = KEY_MAPPING.get(command)
                press_button(control_data, 0.5)
        else:
            logger.info(f"{command} command not support!")


from multiprocessing import Process, Manager


G_PAGE_DATA = None
G_RUN = None


def ocr_screen(page_data, run):
    """截图并识别"""
    while run:
        screenshot()
        text = ocr()
        page_data["text"] = text


def start_ocr():
    global G_PAGE_DATA
    global G_RUN

    with Manager() as manager:
        G_PAGE_DATA = manager.dict()
        G_RUN = manager.Event()
        G_RUN.set()
        p = Process(target=ocr_screen, args=(G_PAGE_DATA, G_RUN))
        p.start()
        p.join()


def main():
    global G_RACE_RUN_EVENT
    global G_RACE_QUIT_EVENT
    global G_IS_ALIVE

    G_RACE_QUIT_EVENT.set()
    G_IS_ALIVE.set()

    init_controller()
    start_ocr()
    start_keep_alive()
    command_input()


if __name__ == "__main__":
    main()

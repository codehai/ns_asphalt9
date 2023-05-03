import datetime
import re
import shutil
import threading
import time
import traceback

from ocr import ocr, Page
from screenshot import screenshot
from utils.controller import Buttons, pro
from utils.log import logger
from utils.timer import Timer


FINISHED_COUNT = 0

# 是否初始化车所在位置
INITED_CAR_POSITION = False

# 程序运行
G_RUN = threading.Event()

# 退出循环事件
G_RACE_RUN_EVENT = threading.Event()
G_RACE_QUIT_EVENT = threading.Event()

# 是否活跃状态
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


def auto_select_car(reverse=False):
    """自动选车"""
    global INITED_CAR_POSITION
    global SELECT_COUNT
    logger.info("Auto select car.")
    # 车库重置到第一辆车
    if reverse and not INITED_CAR_POSITION:
        for i in range(5):
            pro.press_button(Buttons.DPAD_RIGHT, 0.1)
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
                pro.press_button(action, 0.2)
            time.sleep(2)
            SELECT_COUNT = -1

        # 检查车辆是否可用
        pro.press_a()
        text = wait_for("TOP SPEED|HANDLING")
        if has_text("GET KEY", text):
            pro.press_b()
            wait_for("CAR SELECTION")
            SELECT_COUNT += 1
            pro.press_button(select_action[SELECT_COUNT], 2)
            continue

        # 处理跳到第一辆车的情况, 重置车的位置
        if has_text("EMIRA", text):
            pro.press_b(3)
            wait_for("CAR SELECTION")

            # 重置
            action = Buttons.DPAD_RIGHT if reverse else Buttons.DPAD_LEFT
            for i in range(5):
                pro.press_button(action, 0.2)
            time.sleep(2)

            # 快进select
            for step in range(SELECT_COUNT + 1):
                pro.press_button(select_action[step], 0.2)
            time.sleep(2)
            pro.press_a()

        pro.press_a(5)
        page = ocr_screen()
        # 点两下a能开始比赛说明车可用
        if page.name == Page.searching:
            return

        for i in range(2):
            if page.name == Page.car_info:
                pro.press_b(3)
            if page.name == Page.select_car:
                break
            page = ocr_screen()

        SELECT_COUNT += 1
        pro.press_button(select_action[SELECT_COUNT], 2)


def select_car(row, column, confirm=1, reset_count=25):
    """开始比赛并选择车
    row 第几行
    column 第几列
    row: 1 column: 4 选择第1行第4列那辆车
    """
    logger.info("Start select car.")
    # 车库重置到第一辆车
    for i in range(reset_count):
        pro.press_button(Buttons.DPAD_LEFT, 0)

    for i in range(3):
        pro.press_button(Buttons.DPAD_UP, 0)

    # 选车
    for i in range(row):
        pro.press_button(Buttons.DPAD_DOWN, 0)

    for i in range(column - 1):
        pro.press_button(Buttons.DPAD_RIGHT, 0)

    time.sleep(2)

    if confirm:
        confirm_and_play()


def confirm_and_play():
    # 确认车辆
    logger.info("Confirm car")
    pro.press_a(2)
    # 开始比赛
    logger.info("Start race")
    pro.press_a(3)


def process_race(race_mode=0):
    global FINISHED_COUNT
    timer = Timer()
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
            logger.info(f"timer.ctime = {timer.ctime}")
            if progress > 0 and not timer.running:
                timer.start()
                timer.reset(progress * 0.55)
            else:
                if timer.ctime >= 14.5 and timer.ctime <= 15.5:
                    pro.press_buttons(Buttons.B, 6, block=False)
                elif timer.ctime >= 17 and timer.ctime <= 19:
                    pro.press_buttons(Buttons.DPAD_LEFT)
                elif timer.ctime >=21 and timer.ctime <= 22:
                    pro.press_buttons(Buttons.Y)
                    pro.press_buttons(Buttons.Y)
                else:
                    pro.press_button(Buttons.Y, 0.7)
                    pro.press_button(Buttons.Y, 0)
        else:
            pro.press_button(Buttons.Y, 0.7)
            pro.press_button(Buttons.Y, 0)

        if page.name in [Page.race_score, Page.race_results]:
            break

    FINISHED_COUNT += 1
    logger.info(f"Already finished {FINISHED_COUNT} times loop count = {i}.")


def car_hunt(race_mode=0):
    """寻车"""
    logger.info("Start process car hunt.")
    pro.press_a(3)
    logger.info("Wait for select car")
    wait_for("CAR SELECTION")
    logger.info("Start select car")
    select_car(2, 5, confirm=0)
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


def limited_series():
    pro.press_a(3)
    wait_for("CAR SELECTION")
    logger.info("Start select car")
    select_car(2, 5, confirm=1, reset_count=5)

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
            "pages": [Page.multi_player, Page.series],
            "action": pro.press_button,
            "args": (Buttons.A, 3),
        },
        {
            "pages": [Page.limited_series],
            "action": limited_series,
            "args": (),
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
            "pages": [Page.select_car],
            "action": select_car,
            "args": (1, 4),
        },
        # "auto_select_cat": {
        #     "identity": "CAR SELECTION",
        #     "action": auto_select_car,
        #     "args": (1,),
        # },
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

    while G_RACE_RUN_EVENT.is_set() and G_RUN.is_set():
        try:
            page = ocr_screen()
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
            if G_RACE_RUN_EVENT.is_set():
                logger.info("Please stop event loop first.")
            else:
                control_data = KEY_MAPPING.get(command)
                pro.press_buttons(control_data)
                screenshot()
        else:
            logger.info(f"{command} command not support!")


def start_command_input():
    t = threading.Thread(target=command_input, args=())
    t.start()


def main():
    global G_RACE_RUN_EVENT
    global G_RACE_QUIT_EVENT

    G_RACE_QUIT_EVENT.set()
    G_RUN.set()

    start_command_input()

    while G_RUN.is_set():
        if G_RACE_RUN_EVENT.is_set():
            event_loop()
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()

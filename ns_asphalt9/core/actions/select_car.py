import time

from .. import consts, globals, tasks
from ..actions import process_race
from ..controller import Buttons, pro
from ..ocr import ocr_screen
from ..utils.log import logger


def world_series_reset():
    division = globals.DIVISION
    if not division:
        division = "青铜"
    config = globals.CONFIG["多人一"][division]
    level = config["车库等级"]
    left_count_mapping = {"青铜": 4, "白银": 3, "黄金": 2, "铂金": 1}
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
    division = globals.DIVISION
    if not division:
        division = "青铜"
    config = globals.CONFIG["多人一"][division]
    return config["车库位置"]

def mp3_position():
    return globals.CONFIG["多人三"]["车库位置"]

def other_series_position():
    return globals.CONFIG["多人二"]["车库位置"]


def carhunt_position():
    return globals.CONFIG["寻车"]["车库位置"]


def get_race_config():
    mode = globals.MODE if globals.MODE else globals.CONFIG["模式"]
    logger.info(f"Get mode {mode} config.")
    if mode ==  consts.mp3_zh:
        return mp3_position(), other_series_reset, mode
    elif mode == consts.mp2_zh:
        return other_series_position(), other_series_reset, mode
    elif mode == consts.car_hunt_zh:
        return carhunt_position(), carhunt_reset, mode
    elif mode == consts.mp1_zh:
        return world_series_positions(), world_series_reset, mode
    else:
        return default_positions(), default_reset, mode


def select_car():
    # 选车
    logger.info("Start select car.")
    while globals.G_RUN.is_set():
        positions, reset, mode = get_race_config()
        reset()
        if globals.SELECT_COUNT[mode] >= len(positions):
            globals.SELECT_COUNT[mode] = 0
        position = positions[globals.SELECT_COUNT[mode]]

        logger.info(f"Start try position = {position}, count = {globals.SELECT_COUNT[mode]}")

        for i in range(position["row"] - 1):
            pro.press_button(Buttons.DPAD_DOWN, 0)

        for i in range(position["col"] - 1):
            pro.press_button(Buttons.DPAD_RIGHT, 0)

        time.sleep(2)

        pro.press_group([Buttons.A], 2)

        page = ocr_screen()

        # 如果没有进到车辆详情页面, router到默认任务
        if page.name != consts.car_info:
            # TaskManager.task_enter() # TODO
            break

        pro.press_group([Buttons.A], 2)

        page = ocr_screen()

        if page.name in [
            consts.loading_race,
            consts.searching,
            consts.racing,
            consts.loading_carhunt,
        ]:
            break
        elif page.name == consts.tickets:
            pro.press_button(Buttons.DPAD_DOWN, 2)
            pro.press_a(2)
            pro.press_b(2)
            pro.press_a(2)
        else:
            if page.name == consts.car_info and page.has_text(
                "BRONZE|SILVER|GOLD|PLATINUM"
            ):
                globals.DIVISION = ""
            for i in range(2):
                pro.press_b()
                page = ocr_screen()
                if page.name == consts.select_car:
                    break
            globals.SELECT_COUNT[mode] += 1
            continue
    process_race()
    tasks.TaskManager.set_done()

import time

from .. import consts, globals, tasks
from ..controller import Buttons, pro
from ..ocr import ocr_screen
from ..utils.decorator import retry
from ..utils.log import logger


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
    pro.press_group([Buttons.B] * 3, 2)
    pro.press_group([Buttons.DPAD_DOWN] * 4, 0.1)
    pro.press_group([Buttons.DPAD_RIGHT] * 7, 0.1)
    pro.press_group([Buttons.A], 2)
    pro.press_group([Buttons.B], 2)


def in_series(page, mode):
    if (
        mode == consts.mp1_zh
        and page.name == consts.world_series
        or mode in [consts.mp2_zh, consts.mp3_zh]
        and page.name
        in [
            consts.trial_series,
            consts.limited_series,
        ]
    ):
        return True
    return False


@retry(max_attempts=3)
def enter_series(page=None, mode=None):
    """进入多人赛事"""
    if not mode:
        mode = globals.CONFIG["模式"]
    if page and in_series(page, mode):
        return
    reset_to_career()
    pro.press_group([Buttons.ZL] * 4, 0.5)
    if mode == consts.mp2_zh:
        pro.press_group([Buttons.DPAD_DOWN], 0.5)
    if mode == consts.mp3_zh:
        pro.press_group([Buttons.DPAD_DOWN] * 2, 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A], 2)
    page = ocr_screen()
    if in_series(page, mode):
        pass
    else:
        raise Exception(f"Failed to access {mode}, current page = {page.name}")


def _enter_carhunt(page=None, mode=0):
    """进入寻车/传奇寻车
    0 寻车
    1 传奇寻车
    """
    if mode == 0:
        page_name = consts.carhunt
        config_key = "寻车"
        page_feature = "CAR HUNT(?!\sRIOT)"
    else:
        page_name = consts.legendary_hunt
        config_key = "传奇寻车"
        page_feature = "LEGENDARY HUNT(?!\sRIOT)"
    if page:
        logger.info(f"page = {page}, page.name = {page.name}")
    if page and page.name == page_name:
        return
    reset_to_career()
    pro.press_group([Buttons.ZL] * 5, 0.5)
    pro.press_group([Buttons.A], 2)
    pro.press_group([Buttons.ZR] * globals.CONFIG[config_key]["寻车位置"], 0.5)
    time.sleep(1)
    page = ocr_screen()
    if page.has_text(page_feature):
        pro.press_a()
    else:
        pro.press_group([Buttons.ZL] * 12, 0)
        for i in range(20):
            pro.press_group([Buttons.ZR], 0.5)
            page = ocr_screen()
            if page.has_text(page_feature):
                globals.CONFIG[config_key]["寻车位置"] = i + 1
                pro.press_a()
                break
        else:
            raise Exception(f"Failed to access carhunt, current page = {page.name}")


@retry(max_attempts=3)
def enter_carhunt(page=None):
    """进入寻车"""
    _enter_carhunt(page)


@retry(max_attempts=3)
def enter_legend_carhunt(page=None):
    """进入传奇寻车"""
    _enter_carhunt(page, 1)


@retry(max_attempts=3)
def free_pack(page=None):
    """领卡"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.2)
    pro.press_group([Buttons.DPAD_LEFT] * 8, 0.2)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP], 0.5)
    pro.press_group([Buttons.A] * 2, 5)
    page = ocr_screen()
    if page.has_text("CLASSIC PACK.*POSSIBLE CONTENT"):
        pro.press_group([Buttons.A] * 3, 3)
        pro.press_group([Buttons.B], 0.5)
        tasks.TaskManager.set_done()
    else:
        raise Exception(f"Failed to access carhunt, current page = {page.name}")
    

@retry(max_attempts=3)
def prix_pack():
    """大奖赛领卡"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.2)
    pro.press_group([Buttons.DPAD_LEFT] * 6, 0.2)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP] * 8, 0.2)
    if not globals.CONFIG["大奖赛"]["位置"]:
        logger.info("Please set grand prix position!")
        return
    pro.press_group([Buttons.DPAD_DOWN] * globals.CONFIG["大奖赛"]["位置"], 0.5)
    for _ in range(2):
        pro.press_group([Buttons.A], 5)
        page = ocr_screen()
        if page.name == consts.grand_prix:
            pro.press_group([Buttons.DPAD_LEFT] * 4, 0.2)
            pro.press_group([Buttons.DPAD_RIGHT], 0.2)
            pro.press_group([Buttons.A] * 3, 3)
            tasks.TaskManager.set_done()
            break
    else:
        raise Exception(f"Failed to access carhunt, current page = {page.name}")


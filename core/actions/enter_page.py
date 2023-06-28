import time

from core.utils.decorator import retry

from core import consts
from core.controller import Buttons, pro
from core.ocr import ocr_screen
from core import globals
from core.utils.log import logger


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
    pro.press_group([Buttons.A] * 3, 2)
    page = ocr_screen()
    if page.name == consts.career:
        pro.press_group([Buttons.B], 2)
    else:
        raise Exception(f"Failed to access career, current page = {page.name}")


def in_series(page, mode):
    if (
        mode == consts.world_series_zh
        and page.name == consts.world_series
        or mode == consts.other_series_zh
        and page.name
        in [
            consts.trial_series,
            consts.limited_series,
        ]
    ):
        return True
    return False


@retry(max_attempts=3)
def enter_series(page=None, mode=consts.world_series_zh):
    """进入多人赛事"""
    if page and in_series(page, mode):
        return
    reset_to_career()
    pro.press_group([Buttons.ZL] * 4, 0.5)
    if mode != consts.world_series_zh:
        pro.press_group([Buttons.DPAD_DOWN], 0.5)
    time.sleep(2)
    pro.press_group([Buttons.A], 2)
    page = ocr_screen()
    if in_series(page, mode):
        pass
    else:
        raise Exception(f"Failed to access {mode}, current page = {page.name}")


@retry(max_attempts=3)
def enter_carhunt(page=None):
    """进入寻车"""
    logger.info(f"page = {page}, page.name = {page.name}")
    if page and page.name == consts.carhunt:
        return
    reset_to_career()
    pro.press_group([Buttons.ZL] * 5, 0.5)
    pro.press_group([Buttons.A], 2)
    pro.press_group([Buttons.ZR] * globals.CONFIG["寻车"]["位置"], 0.5)
    time.sleep(2)
    page = ocr_screen()
    if page.has_text("CAR HUNT"):
        pro.press_a()
    else:
        pro.press_group([Buttons.ZL] * 12, 0)
        for i in range(20):
            pro.press_group([Buttons.ZR], 1)
            page = ocr_screen()
            if page.has_text("CAR HUNT"):
                globals.CONFIG["寻车"]["位置"] = i + 1
                pro.press_a()
                break
        else:
            raise Exception(f"Failed to access carhunt, current page = {page.name}")


@retry(max_attempts=3)
def free_pack(page=None):
    """领卡"""
    reset_to_career()
    pro.press_group([Buttons.DPAD_DOWN] * 3, 0.5)
    pro.press_group([Buttons.DPAD_LEFT] * 8, 0.5)
    pro.press_group([Buttons.A], 0.5)
    pro.press_group([Buttons.DPAD_UP], 0.5)
    pro.press_group([Buttons.A] * 2, 5)
    page = ocr_screen()
    if page.has_text("CLASSIC PACK.*POSSIBLE CONTENT"):
        pro.press_group([Buttons.A] * 3, 3)
        pro.press_group([Buttons.B], 0.5)
        # TaskManager.set_done() TODO
    else:
        raise Exception(f"Failed to access carhunt, current page = {page.name}")

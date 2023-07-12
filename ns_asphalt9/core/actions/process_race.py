import time

from .. import consts, globals, ocr
from ..controller import Buttons, pro
from ..utils.log import logger


def process_race(race_mode=0):
    logger.info(f"Start racing.")
    for i in range(60):
        progress = 0
        page = ocr.ocr_screen()
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
                while globals.G_RUN.is_set():
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
        elif page.hunt_car == "APEX AP-0" and page.mode == consts.car_hunt_zh:
            if progress > 0:
                start = time.perf_counter()
                delta = progress * 0.55 + 4.5
                while globals.G_RUN.is_set():
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

        if page.name in [consts.race_score, consts.race_results, consts.race_reward, consts.system_error]:
            break

    globals.FINISHED_COUNT += 1
    logger.info(f"Already finished {globals.FINISHED_COUNT} times loop count = {i}.")

import datetime
import os
import re
import shutil

import pytesseract
from PIL import Image

from utils.log import logger


class Page:
    # 游戏加载
    loading_race = "loading_race"
    # 手柄激活
    connect_controller = "connect_controller"
    # 手柄已连接
    connected_controller = "connected_controller"
    # 多人一
    series = "series"
    # 寻车
    carhunt = "carhunt"
    # 选车
    select_car = "select_car"
    # 车辆详情
    car_info = "car_info"
    # 匹配中
    searching = "searching"
    # 比赛中
    racing = "racing"
    # 降级
    demoted = "demoted"
    # 断开连接
    disconnected = "disconnected"
    # 无连接
    no_connection = "no_connection"
    # 俱乐部奖励
    club_reward = "club_reward"
    # 通行证任务完成
    vip_reward = "vip_reward"
    # 比赛成绩
    race_score = "race_score"
    # 比赛奖励
    race_reward = "race_reward"
    # 里程碑奖励
    milestone_reward = "milestone_reward"
    # 连接错误
    connect_error = "connect_error"
    # 升星
    star_up = "star_up"
    # 离线模式
    offline_mode = "offline_mode"
    # 系统错误
    system_error = "system_error"

    features = {
        loading_race: "LOADING RACE",
        connect_controller: "Press.*on the controller",
        connected_controller: "Controllers",
        series: "WORLD SERIES",
        carhunt: "CAR HUNT",
        select_car: "CAR SELECTION",
        car_info: "TOP SPEED|HANDLING|NITRO",
        searching: "SEARCHING",
        racing: "DIST",
        demoted: "DEMOTED",
        disconnected: "DISCONNECTED",
        no_connection: "NO CONNECTION",
        club_reward: "YOUR CLUB ACHIEVED",
        vip_reward: "TIER",
        # CONGRATULATIONS.*IMPROVE,
        race_score: "RATING",
        race_reward: "REPUTATION",
        milestone_reward: "CONGRATULATIONS",
        connect_error: "CONNECTION ERROR",
        star_up: "STAR UP",
        offline_mode: "OFFLINE MODE",
        system_error: "software.*closed",
    }

    @classmethod
    def parse_racing(cls, text):
        pass

    @classmethod
    def has_text(cls, identity, page_text):
        """page_text中是否包含identity"""
        if re.findall(identity, page_text):
            return True
        return False

    @classmethod
    def parse_page(cls, text):
        data = {
            "raw": text,
            "page": {},
        }
        match_pages = []
        for name in cls.features:
            if cls.has_text(cls.features[name], text):
                match_pages.append(name)

        match_page = None
        if not match_pages and text:
            cls.capture()
            return data
        if len(match_pages) > 1:
            cls.capture()
        match_page = match_pages[0]
        data["page"]["name"] = match_page

        if hasattr(cls, f"parse_{match_page}"):
            func = getattr(cls, f"parse_{match_page}")
            data["page"]["data"] = func(text)

        return data

    @classmethod
    def capture():
        filename = (
            "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
        )
        shutil.copy("./images/output.jpg", f"./images/not_match_images/{filename}")
        return filename


def ocr(name="output", path="./images"):
    image_path = os.path.join(path, f"{name}.jpg")
    im = Image.open(image_path)
    string = pytesseract.image_to_string(im, lang="eng", config="--psm 11")
    text = string.replace("\n", " ")
    im.close()
    page_data = Page.parse_page(text)
    logger.info(f"ocr text = {text}, data = {page_data}")
    return text


if __name__ == "__main__":
    ocr()

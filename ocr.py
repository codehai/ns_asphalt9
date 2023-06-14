import datetime
import os
import re
import shutil

import pytesseract
from PIL import Image

from utils.log import logger


class Page:
    # 游戏加载
    loading_game = "loading_game"
    # 比赛加载
    loading_race = "loading_race"
    # 寻车加载
    loading_carhunt = "loading_carhunt"
    # 手柄激活
    connect_controller = "connect_controller"
    # 手柄已连接
    connected_controller = "connected_controller"
    # 多人主页
    multi_player = "multi_player"
    # 多人一
    world_series = "world_series"
    # 多人二
    trial_series = "trial_series"
    # 寻车
    carhunt = "carhunt"
    # 通行证寻车
    legendary_hunt = "legendary_hunt"
    # 购买票
    tickets = "tickets"
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
    # 比赛结果
    race_results = "race_results"
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
    # 服务错误
    server_error = "server_error"
    # switch 主页
    switch_home = "switch_home"
    # 比赛中菜单页
    game_menu = "game_menu"
    # 抽卡页面
    card_pack = "card_pack"
    # 限时赛事
    limited_series = "limited_series"
    # 俱乐部申请
    club = "club"
    # 每日赛事
    daily_events = "daily_events"
    # 没匹配到对手
    no_opponents = "no_opponents"
    # 生涯
    career = "career"

    # 页面特征
    features = {
        loading_game: "GAMELOFT PLAYER ID.*ASPHALT",
        loading_race: "LOADING RACE",
        connect_controller: "Press.*on the controller",
        connected_controller: "Controllers",
        multi_player: "WORLD SERIES.*(LIMITED|TRIAL) SERIES",
        daily_events: "PLAY LIMITED.*BEST WAY TO EARN CREDITS FAST",
        world_series: "WORLD SERIES|MY POSITION|SERIES SCORE|NEXT MILESTONE|LEADERBOARD|PLAY",
        limited_series: "LIMITED SERIES|MY POSITION|SERIES SCORE|NEXT MILESTONE|LEADERBOARD|PLAY",
        trial_series: "TRIAL SERIES|MY POSITION|SERIES SCORE|NEXT MILESTONE|LEADERBOARD|PLAY",
        carhunt: "CAR HUNT:.*CAR HUNT EVENT PACK",
        loading_carhunt: "CAR HUNT.*BEST TIME",
        legendary_hunt: "LEGENDARY HUNT",
        tickets: "TICKETS",
        select_car: "CAR SELECTION",
        car_info: "TOP SPEED|ACCELERATION|HANDLING|NITRO|TOUCH|PLAY",
        searching: "SEARCHING FOR OTHER PLAYERS AND LOCATION",
        demoted: "DEMOTED",
        disconnected: "DISCONNECTED",
        no_connection: "NO CONNECTION",
        club_reward: "YOUR CLUB ACHIEVED",
        vip_reward: "TIER",
        # CONGRATULATIONS.*IMPROVE,
        racing: "POS\.| \d/\d|DIST|\d+%|NITRO|\d+:\d+\.\d+|TOUCHORIVE|SURFING|PERFECT",
        race_results: "RACE RESULTS|POS\.|PLAYER|CAR NAME|NEXT",
        race_score: "WINNER|YOUR POSITION|YOUR TIME|RATING|NEXT",
        race_reward: "RACE|REWARDS|REPUTATION|TOTAL|CREDITS|NEXT",
        milestone_reward: "CONGRATULATIONS",
        connect_error: "CONNECTION ERROR",
        star_up: "STAR|UP",
        offline_mode: "OFFLINE MODE",
        system_error: "software.*closed",
        server_error: "ERROR.*ACTION",
        game_menu: "GAME MENU",
        switch_home: "Asphalt 9: Legends.*ASPHALT",
        card_pack: "CARD PACK LEVEL INFO",
        club: "YOUR CLUB",
        no_opponents: "NO OPPONENTS WERE FOUND",
        career: "COLLECTED.*CAREER",
    }

    # 部分匹配的页面
    part_match = [
        world_series,
        limited_series,
        trial_series,
        car_info,
        racing,
        race_results,
        race_score,
        race_reward,
        star_up,
    ]

    text = None
    name = None
    data = None

    mode = None
    division = None
    touchdriver = None

    def prepare(self):
        self.text = self.text.replace("\n", " ")
        self.name = None
        self.data = None

    def parse_common(self):
        divisions = re.findall("BRONZE|SILVER|GOLD|PLATINUM", self.text)
        if divisions and self.name in [
            self.world_series,
            self.searching,
            self.loading_race,
        ]:
            self.division = divisions[0]

        modes = re.findall(
            "CAR HUNT|WORLD SERIES|LIMITED SERIES|TRIAL SERIES", self.text
        )
        if modes and self.name not in [self.multi_player]:
            self.mode = modes[0]

        if "TOUCHDRIVE ON" in self.text:
            self.touchdriver = 1
        if "TOUCHDRIVE OFF" in self.text:
            self.touchdriver = 0

    def parse_racing(self):
        position = re.findall(r"\d/\d", self.text)
        position = position[0] if position else None
        progress = re.findall(r"(\d+)%", self.text)
        progress = int(progress[0]) if progress else None

        self.data = {
            "position": position,
            "progress": progress,
        }

    def has_text(self, name):
        """page_text中是否包含identity"""
        match_count = len(re.findall(self.features[name], self.text))
        if name not in self.part_match and match_count > 0:
            match_count = 10
        return match_count

    def parse_page(self, text):
        self.text = text
        last_page_name = self.name
        self.prepare()
        match_pages = []
        for name in self.features:
            match_count = self.has_text(name)
            if match_count > 0:
                if last_page_name == self.racing:
                    match_count += 1
                match_pages.append((name, match_count))

        match_pages.sort(key=lambda pages: pages[1], reverse=True)

        if last_page_name in [self.loading_race, self.racing] and not match_pages:
            match_pages.append((last_page_name, 1))

        if (
            not match_pages
            and self.text
            or len(match_pages) >= 2
            and match_pages[0][1] == match_pages[1][1]
        ):
            logger.info(f"match_pages = {match_pages}")
            self.capture()

        if match_pages:
            self.name = match_pages[0][0]

            self.parse_common()

            if hasattr(self, f"parse_{self.name}"):
                func = getattr(self, f"parse_{self.name}")
                func()

    def capture(self):
        filename = (
            "".join([str(d) for d in datetime.datetime.now().timetuple()]) + ".jpg"
        )
        shutil.copy("./images/output.jpg", f"./images/not_match_images/{filename}")
        return filename

    @property
    def dict(self):
        return {
            "name": self.name,
            "text": self.text,
            "data": self.data,
            "mode": self.mode,
            "division": self.division,
            "touchdriver": self.touchdriver,
        }


page = Page()


def ocr(name="output", path="./images"):
    image_path = os.path.join(path, f"{name}.jpg")
    im = Image.open(image_path)
    text = pytesseract.image_to_string(im, lang="eng", config="--psm 11")
    im.close()
    page.parse_page(text)
    logger.info(f"ocr page dict = {page.dict}")
    return page


if __name__ == "__main__":
    ocr()

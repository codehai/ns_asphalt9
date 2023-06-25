import re

from core import actions, consts
from core.controller import Buttons, pro
from core.utils.decorator import cache_decorator


class Page:
    text = None
    name = None
    data = None
    mode = None
    division = None
    touchdriver = None

    feature = ""
    part_match = False

    action = None
    args = ()

    def __init__(self, last_page: "Page", text: str) -> None:
        if last_page:
            self.mode = last_page.mode
            self.division = last_page.division
            self.touchdriver = last_page.touchdriver
        self.text = text

    def parse_common(self):
        divisions = re.findall("BRONZE|SILVER|GOLD|PLATINUM", self.text)
        if divisions and self.name in [
            consts.world_series,
            consts.searching,
            consts.loading_race,
        ]:
            self.division = divisions[0]

        modes = re.findall(
            "CAR HUNT|WORLD SERIES|LIMITED SERIES|TRIAL SERIES", self.text
        )
        if modes and self.name not in [consts.multi_player]:
            self.mode = modes[0]

        if "TOUCHDRIVE ON" in self.text:
            self.touchdriver = 1
        if "TOUCHDRIVE OFF" in self.text:
            self.touchdriver = 0

    @classmethod
    def calc_weight(cls, text: str) -> int:
        match_count = len(re.findall(cls.feature, text))
        if cls.part_match and match_count > 0:
            match_count = 10
        return match_count

    def has_text(self, identity):
        """page_text中是否包含identity"""
        if re.findall(identity, self.text):
            return True
        return False

    @property
    def dict(self) -> dict:
        return {
            "name": self.name,
            "text": self.text,
            "data": self.data,
            "mode": self.mode,
            "division": self.division,
            "touchdriver": self.touchdriver,
        }

    def call_action(self):
        if self.action:
            self.action(*self.args)


@cache_decorator("page")
class Empty(Page):
    """游戏加载页"""

    name = consts.empty


@cache_decorator("page")
class LoadingGame(Page):
    """游戏加载页"""

    name = consts.loading_game
    feature = "GAMELOFT PLAYER ID.*ASPHALT"
    part_match = False


@cache_decorator("page")
class LoadingRace(Page):
    """比赛加载页"""

    name = consts.loading_race
    feature = "LOADING RACE"
    part_match = False

    action = actions.process_race


@cache_decorator("page")
class LoadingCarHunt(Page):
    """寻车加载页"""

    name = consts.loading_carhunt
    feature = "CAR HUNT.*BEST TIME"
    part_match = False


@cache_decorator("page")
class ConnectController(Page):
    """连接手柄"""

    name = consts.connect_controller
    feature = "Press.*on the controller"
    part_match = False

    action = actions.connect_controller


@cache_decorator("page")
class ConnectedController(Page):
    """手柄已连接"""

    name = consts.connected_controller
    feature = "Controllers"
    part_match = False

    action = actions.enter_game


@cache_decorator("page")
class MultiPlayer(Page):
    """多人首页"""

    name = consts.multi_player
    feature = "WORLD SERIES.*(LIMITED|TRIAL) SERIES"
    part_match = False

    action = actions.enter_series


@cache_decorator("page")
class WorldSeries(Page):
    """多人一"""

    name = consts.world_series
    feature = "WORLD SERIES|MY POSITION|SERIES SCORE|NEXT MILESTONE|LEADERBOARD|PLAY"
    part_match = True

    action = pro.press_button
    args = (Buttons.A, 3)


@cache_decorator("page")
class TrialSeries(Page):
    """多人二尾流"""

    name = consts.trial_series
    feature = "TRIAL SERIES|MY POSITION|SERIES SCORE|NEXT MILESTONE|LEADERBOARD|PLAY"
    part_match = True

    action = pro.press_button
    args = (Buttons.A, 3)


@cache_decorator("page")
class LimitedSeries(Page):
    """多人二限时赛事"""

    name = consts.limited_series
    feature = "LIMITED SERIES|MY POSITION|SERIES SCORE|NEXT MILESTONE|LEADERBOARD|PLAY"
    part_match = True

    action = pro.press_button
    args = (Buttons.A, 3)


@cache_decorator("page")
class CarHunt(Page):
    """寻车"""

    name = consts.carhunt
    feature = "CAR HUNT:.*CAR HUNT EVENT PACK"
    part_match = False

    action = pro.press_button
    args = (Buttons.A, 3)


@cache_decorator("page")
class LegendaryHunt(Page):
    """通行证寻车"""

    name = consts.legendary_hunt
    feature = "LEGENDARY HUNT"
    part_match = False


@cache_decorator("page")
class Tickets(Page):
    """购买票"""

    name = consts.tickets
    feature = "TICKETS"
    part_match = False


@cache_decorator("page")
class SelectCar(Page):
    """选车"""

    name = consts.select_car
    feature = "CAR SELECTION"
    part_match = False

    action = actions.select_car


@cache_decorator("page")
class CarInfo(Page):
    """车辆详情"""

    name = consts.car_info
    feature = "TOP SPEED|ACCELERATION|HANDLING|NITRO|TOUCH|PLAY"
    part_match = True

    action = pro.press_button
    args = (Buttons.A, 3)


@cache_decorator("page")
class Searching(Page):
    """匹配中"""

    name = consts.searching
    feature = "SEARCHING FOR OTHER PLAYERS AND LOCATION"
    part_match = False

    action = pro.press_button
    args = (Buttons.Y, 3)


@cache_decorator("page")
class Racing(Page):
    """比赛中"""

    name = consts.racing
    feature = "POS\.| \d/\d|DIST|\d+%|NITRO|\d+:\d+\.\d+|TOUCHORIVE|SURFING|PERFECT"
    part_match = True

    def parse_racing(self):
        position = re.findall(r"\d/\d", self.text)
        position = position[0] if position else None
        progress = re.findall(r"(\d+)%", self.text)
        progress = int(progress[0]) if progress else None

        self.data = {
            "position": position,
            "progress": progress,
        }


@cache_decorator("page")
class Demoted(Page):
    """降级"""

    name = consts.demoted
    feature = "DEMOTED"
    part_match = False

    action = actions.demoted


@cache_decorator("page")
class Disconnected(Page):
    """断开连接"""

    name = consts.disconnected
    feature = "DISCONNECTED"
    part_match = False

    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class NoConnection(Page):
    """无连接"""

    name = consts.no_connection
    feature = "NO CONNECTION"
    part_match = False
    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class ClubReward(Page):
    """俱乐部奖励"""

    name = consts.club_reward
    feature = "YOUR CLUB ACHIEVED"
    part_match = False

    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class VipReward(Page):
    """通行证任务完成"""

    name = consts.vip_reward
    feature = "TIER"
    part_match = False
    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class RaceResults(Page):
    """比赛结果"""

    name = consts.race_results
    feature = "RACE RESULTS|POS\.|PLAYER|CAR NAME|NEXT"
    part_match = True
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class RaceScore(Page):
    """比赛成绩"""

    name = consts.race_score
    feature = "WINNER|YOUR POSITION|YOUR TIME|RATING|NEXT"
    part_match = True
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class RaceReward(Page):
    """比赛奖励"""

    name = consts.race_reward
    feature = "RACE|REWARDS|REPUTATION|TOTAL|CREDITS|NEXT"
    part_match = True
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class MilestoneReward(Page):
    """里程碑奖励"""

    name = consts.milestone_reward
    feature = "CONGRATULATIONS"
    part_match = False
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class ConnectError(Page):
    """连接错误"""

    name = consts.connect_error
    feature = "CONNECTION ERROR"
    part_match = False
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class StarUp(Page):
    """升星"""

    name = consts.star_up
    feature = "STAR|UP"
    part_match = True
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class OfflineMode(Page):
    """离线模式"""

    name = consts.offline_mode
    feature = "OFFLINE MODE"
    part_match = False
    action = pro.press_group
    args = ([Buttons.DPAD_LEFT, Buttons.B], 1)


@cache_decorator("page")
class SystemError(Page):
    """系统错误"""

    name = consts.system_error
    feature = "software.*closed"
    part_match = False

    action = (pro.press_group,)
    args = ([Buttons.A] * 3, 3)


@cache_decorator("page")
class ServerError(Page):
    """服务错误"""

    name = consts.server_error
    feature = "ERROR.*ACTION"
    part_match = False
    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class SwitchHome(Page):
    """switch 主页"""

    name = consts.switch_home
    feature = "Asphalt 9: Legends.*ASPHALT"
    part_match = False

    action = (pro.press_group,)
    args = ([Buttons.A] * 3, 3)


@cache_decorator("page")
class GameMenu(Page):
    """比赛中菜单页"""

    name = consts.game_menu
    feature = "GAME MENU"
    part_match = False
    action = pro.press_button
    args = (Buttons.A,)


@cache_decorator("page")
class CardPack(Page):
    """抽卡页面"""

    name = consts.card_pack
    feature = "CARD PACK LEVEL INFO"
    part_match = False

    action = (pro.press_group,)
    args = ([Buttons.B] * 2, 3)


@cache_decorator("page")
class Club(Page):
    """俱乐部申请"""

    name = consts.club
    feature = "YOUR CLUB"
    part_match = False
    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class DailyEvents(Page):
    """每日赛事"""

    name = consts.daily_events
    feature = "PLAY LIMITED.*BEST WAY TO EARN CREDITS FAST"
    part_match = False

    action = actions.enter_carhunt


@cache_decorator("page")
class NoOpponents(Page):
    """每日赛事"""

    name = consts.no_opponents
    feature = "NO OPPONENTS WERE FOUND"
    part_match = False
    action = pro.press_button
    args = (Buttons.B,)


@cache_decorator("page")
class Career(Page):
    """生涯"""

    name = consts.career
    feature = "COLLECTED.*CAREER"
    part_match = False
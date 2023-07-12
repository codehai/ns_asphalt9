import threading

from . import consts, globals, actions
from .utils.log import logger


class TaskManager:
    timers = []
    status = consts.TaskStatus.default
    current_task = ""

    @classmethod
    def task_init(cls):
        if "任务" not in globals.CONFIG:
            return
        for task in globals.CONFIG["任务"]:
            if task["运行"] > 0:
                timer = cls.task_producer(task["名称"], task["间隔"])
                cls.timers.append(timer)
        globals.task_queue.put(globals.CONFIG["模式"])

    @classmethod
    def task_producer(cls, task, duration, skiped=False):
        if skiped:
            globals.task_queue.put(task)
        else:
            logger.info(f"Start task {task} producer, duration = {duration}min")
            skiped = True
        timer = threading.Timer(
            duration * 60, cls.task_producer, (task, duration), {"skiped": skiped}
        )
        timer.start()
        return timer

    @classmethod
    def task_dispatch(cls, page) -> None:
        if "任务" not in globals.CONFIG:
            return False

        if page.name not in [
            consts.world_series,
            consts.limited_series,
            consts.trial_series,
            consts.carhunt,
            consts.card_pack,
            consts.legend_pass,
            consts.legendary_hunt,
            consts.daily_events,
            consts.multi_player
        ]:
            return False

        if globals.task_queue.empty():
            if cls.status == consts.TaskStatus.done:
                cls.task_enter(globals.CONFIG["模式"], page=page)
                cls.status = consts.TaskStatus.default
                return True
        else:
            task = globals.task_queue.get()
            logger.info(f"Get {task} task from queue.")
            cls.status = consts.TaskStatus.start
            cls.current_task = task
            cls.task_enter(task, page)
            return True

    @classmethod
    def task_enter(cls, task, page=None) -> None:
        logger.info(f"Start process {task} task.")
        if task in [consts.mp1_zh, consts.mp2_zh, consts.mp3_zh]:
            actions.enter_series(page=page)
        if task == consts.car_hunt_zh:
            actions.enter_carhunt(page=page)
        if task == consts.free_pack_zh:
            actions.free_pack()
        if task == consts.prix_pack_zh:
            actions.prix_pack()
        if task == consts.legendary_hunt_zh:
            actions.enter_legend_carhunt()

    @classmethod
    def set_done(cls) -> None:
        if cls.status == consts.TaskStatus.start:
            cls.status = consts.TaskStatus.done
            cls.current_task = ""

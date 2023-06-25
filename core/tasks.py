import threading

from core import consts, globals
from core.actions import enter_carhunt, enter_series, free_pack
from core.pages import Page
from core.utils.log import logger


class TaskManager:
    timers = []
    status = consts.TaskStatus.default
    current_task = ""

    @classmethod
    def task_init(cls):
        if "任务" not in globals.CONFIG:
            return
        for task in globals.CONFIG["任务"]:
            if task["间隔"] > 0:
                timer = cls.task_producer(task["名称"], task["间隔"])
                cls.timers.append(timer)
        cls.task_enter()

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
    def task_dispatch(cls, page: Page) -> None:
        if "任务" not in globals.CONFIG:
            return False

        if page.name not in [
            consts.world_series,
            consts.limited_series,
            consts.trial_series,
            consts.carhunt,
            consts.card_pack,
        ]:
            return False

        if globals.task_queue.empty():
            if cls.status == consts.TaskStatus.done:
                cls.task_enter()
                cls.status = consts.TaskStatus.default
                return True
        else:
            task = globals.task_queue.get()
            logger.info(f"Get {task} task from queue.")
            cls.status = consts.TaskStatus.start
            cls.current_task = task
            cls.task_enter(task)
            return True

    @classmethod
    def task_enter(cls, task: str = "") -> None:
        if not task:
            task = globals.CONFIG["task"]
        logger.info(f"Start process {task} task.")
        if task == consts.TaskName.world_series:
            enter_series()
        if task == consts.TaskName.other_series:
            enter_series(task)
        if task == consts.TaskName.car_hunt:
            enter_carhunt()
        if task == consts.TaskName.free_pack:
            free_pack()

    @classmethod
    def set_done(cls) -> None:
        if cls.status == consts.TaskStatus.start:
            cls.status = consts.TaskStatus.done
            cls.current_task = ""

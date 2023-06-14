import threading
import queue

q = queue.Queue()

CONFIG = []


class TaskManager:
    world_series = "world_series"
    other_series = "other_series"
    car_hunt = "car_hunt"
    free_pack = "free_pack"

    current_task = None

    def __init__(self) -> None:
        # self.task_producer("test task", 3)
        if "a" not in CONFIG:
            print("11111111")

    def log_global(self):
        print(CONFIG)

    def task_producer(self, task, duration, skiped=False):
        if skiped:
            print(f"put {task}")
            q.put(task)
        else:
            skiped = True
        timer = threading.Timer(
            duration * 1, self.task_producer, (task, duration), {"skiped": skiped}
        )
        timer.start()

    def task_consumer(self):
        while True:
            t = q.get_nowait()
            print(f"get task {t}")


t = TaskManager()
CONFIG.append(123)
t.log_global()
# t.task_consumer()

# print(q.empty())

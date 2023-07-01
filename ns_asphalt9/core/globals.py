import multiprocessing
import queue
import threading

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()

task_queue = queue.Queue()


CONFIG = None

FINISHED_COUNT = 0

# 程序运行
G_RUN = threading.Event()

#
G_OUT_WORKER = threading.Event()

# 退出循环事件
G_RACE_RUN_EVENT = threading.Event()
G_RACE_QUIT_EVENT = threading.Event()

# 是否活跃状态
NO_OPERATION_COUNT = 0

# 游戏模式
MODE = ""

# 段位
DIVISION = ""

# 选车次数
SELECT_COUNT = 0
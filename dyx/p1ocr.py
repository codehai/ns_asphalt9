"""
多人1+图像采集ocr监控
"""

import nxbt
import dyxocr
import dyxnx
import time
import random
import os


# Start the NXBT service
nx = nxbt.Nxbt()

# Create a Pro Controller and wait for it to connect
controller_index = nx.create_controller(
    nxbt.PRO_CONTROLLER,
    reconnect_address=nx.get_switch_addresses())

nx.wait_for_connection(controller_index)
print('success connect bluetooth')

# 重连手柄
mconnect = """
L R 0.5s
1s
L R 0.5s
1s
A 0.5s
2s
"""

# Run a macro on the Pro Controller
nx.macro(controller_index, mconnect)
print('success connect game')

# 退回主界面后再进入多1赛事界面
begin_tag = dyxnx.to_mp1_page(nx,controller_index)
restart_tag = 0

# 循环赛事
for i in range(500):
    print(f'running time {i}')

    # 累计5次错误后重启游戏
    while restart_tag == 5:
        # 重启游戏并进入主界面
        restart_tag = dyxnx.restart_game(nx,controller_index)
        begin_tag = 1
    
    # 从多1赛事界面开始，结束一次赛事后返回多1赛事界面
    if begin_tag == 0:
        restart_tag = 0
        begin_tag = dyxnx.mp1_race_DS(nx,controller_index)
    else:
        restart_tag += 1
        # 退回主界面后再进入多1赛事界面
        begin_tag = dyxnx.to_mp1_page(nx,controller_index)

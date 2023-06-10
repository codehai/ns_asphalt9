"""
寻车+图像采集ocr监控
"""

import nxbt
import dyxnx
import dyxocr


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

# 退回主界面后再进入寻车赛事界面
begin_tag = dyxnx.to_car_hunt_page(nx, controller_index)
restart_tag = 0

# 循环寻车赛事
for i in range(500):

    print(f'running time {i}')

    # 累计5次错误后重启游戏
    while restart_tag == 5:

        # 重启游戏并进入主界面
        restart_tag = dyxnx.restart_game(nx, controller_index)
        begin_tag = 1

    # 从寻车赛事界面开始，结束一次赛事后返回寻车赛事界面
    if begin_tag == 0:

        # 重置重启标志
        restart_tag = 0

        # 用NSX寻车，结束后回到寻车赛事界面
        begin_tag, oil_tag, ticket_tag = dyxnx.car_hunt_race(nx, controller_index, 'NSX')

        # 如果没回到寻车赛事界面，结束当次循环直接进入下次的else部分
        if begin_tag == 1:
            continue

        # 若没票了则补票 7 min
        if ticket_tag <= 1:
            print('waiting for tickets')
            for i in range(7):
                nx.press_buttons(controller_index, [nxbt.Buttons.DPAD_DOWN], down=0.2, up=60)

        # 如果油量用尽则等待补油
        if oil_tag <= 1:
            dyxnx.wait_for_oil(nx, controller_index, 'NSX')
    else:
        restart_tag += 1
        # 退回主界面后再进入寻车赛事界面
        begin_tag = dyxnx.to_car_hunt_page(nx, controller_index)

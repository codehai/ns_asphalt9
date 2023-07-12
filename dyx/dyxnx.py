"""
多人1+图像采集ocr监控
"""

import nxbt
from nxbt import Buttons
from nxbt import Sticks
import time
import dyxocr


# 重启游戏
def restart_game(nx, controller_index):

    # 回到ns主界面
    print('return to ns homepage')
    for i in range(5):

        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=1)
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=1)
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=1)

        # 回到ns主界面
        nx.press_buttons(controller_index, [Buttons.HOME])
        # 定位到最上行
        nx.press_buttons(controller_index, [Buttons.DPAD_UP], down=0.2, up=1)
        nx.press_buttons(controller_index, [Buttons.DPAD_UP], down=0.2, up=1)
        # 定位到中间行
        nx.press_buttons(controller_index, [Buttons.DPAD_DOWN], down=0.2, up=1)
        # 定位到最左边第一个游戏，若无误，则应为asphalt
        nx.press_buttons(controller_index, [Buttons.DPAD_LEFT], down=5, up=0.5)
        # 检查定位是否成功
        tag = dyxocr.check_ns()
        if tag == 0:
            print('return success')
            break

    # 无法回到ns主界面，返回错误 5（重启标志）
    if i == 4:
        print('err retrun to ns homepage')
        return 5

    # 关闭并重启asphalt
    print('restart asphalt')
    nx.press_buttons(controller_index, [Buttons.X], down=0.2, up=1)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)

    # 检测是否回到asphalt主界面
    for i in range(30):
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=10)
        tag = dyxocr.check_asphalt()
        if tag == 0:
            return 0

    # 无法重启asphlat，返回错误 5（重启标志）
    print('err restart game')
    return 5


# 退回主界面后再进入寻车赛事界面
def to_car_hunt_page(nx,controller_index):

    # 退回主界面
    print('exit to asphalt mainpage')
    for i in range(4):
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=5)
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=1)
    
    # 定位每日赛事主界面
    print('try to find daily mainpage')
    nx.press_buttons(controller_index, [Buttons.ZL], down=0.2, up=0.5)
    for i in range(10):
        nx.press_buttons(controller_index, [Buttons.ZR], down=0.2, up=0.5)
        tag = dyxocr.is_daily()
        if tag == 0:
            print('find daily mainpage !')
            break

    # 无法定位每日赛事界面，返回错误 1
    if i==9:
        print('err cannot find daily mainpage')
        img = dyxocr.screenshot()
        dyxocr.save_img(img, 'err_find_daily_mainpage')
        return 1

    # 进入每日赛事，定位寻车赛事
    print('try to find car hunt page')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)
    nx.press_buttons(controller_index, [Buttons.ZL], down=0.2, up=5)
    for i in range(20):
        nx.press_buttons(controller_index, [Buttons.ZR], down=0.2, up=0.5)
        tag = dyxocr.is_car_hunt()
        if tag == 0:
            print('find car hunt page !')
            break
    
    # 无法定位寻车赛事，返回错误 2
    if i == 19:
        print('err cannot find car hunt page')
        img = dyxocr.screenshot()
        dyxocr.save_img(img, 'err_find_car_hunt_page')
        return 2
    
    # 进入寻车赛事
    print('enter car hunt page')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)

    return dyxocr.check_car_hunt_page()


# 从寻车赛事界面开始
def car_hunt_race(nx,controller_index,car):

    # 进入具体车辆界面
    print('enter car page')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)

    # 检查车辆，油量，票数
    print('check car and oil')
    tag, oil_tag = dyxocr.check_car(car)
    ticket_tag = dyxocr.check_tickets()

    # 车辆错误或油量错误或票数错误，取消比赛
    if tag == 1 or oil_tag == 0 or ticket_tag == 0:
        print('return to car hunt page')
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=5)
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=5)
        print('check car hunt page')
        tag = dyxocr.check_car_hunt_page()
        
        return tag, oil_tag, ticket_tag
    
    # 车辆正确，开始比赛
    print('wait for start')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)
    time.sleep(10)

    print('start')
    for i in range(1,15):
        nx.press_buttons(controller_index, [Buttons.ZL], down=1, up=0.2)
        nx.press_buttons(controller_index, [Buttons.Y], down=0.2, up=0.5)
        nx.press_buttons(controller_index, [Buttons.Y], down=0.2, up=0.5)

        tag = dyxocr.check_car_hunt_race()
        if tag == 0:
            break

    # 比赛结束，退回到寻车赛事界面
    print('return to car hunt page')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=30)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=30)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=30)

    # 检查寻车赛事界面
    print('check car hunt page')
    tag = dyxocr.check_car_hunt_page()

    return tag, oil_tag, ticket_tag


# 根据车辆决定补油时长
def wait_for_oil(nx,controller_index, car):

    print('waiting for oil')

    if 'DS' in car:
        return 0
    elif 'NSX' in car: 
        for i in range(12): # 12 min
            nx.press_buttons(controller_index, [Buttons.DPAD_DOWN], down=0.5, up=60)
        return 0
    else:
        print(f'err {car}')
        return 0


# 退回主界面后再进入多1赛事界面
def to_mp1_page(nx,controller_index):

    # 退回主界面
    print('exit to asphalt mainpage')
    for i in range(1, 5):
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=5)
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=1)
    
    # 通过定位每日赛事来定位多1
    print('try to find daily mainpage')
    nx.press_buttons(controller_index, [Buttons.ZL], down=0.2, up=0.5)

    for i in range(10):
        nx.press_buttons(controller_index, [Buttons.ZR], down=0.2, up=0.5)
        tag = dyxocr.is_daily()
        if tag == 0:
            print('find daily mainpage !')
            break

    # 无法定位每日赛事界面，返回错误 1
    if i==9:
        print('err cannot find daily mainpage')
        img = dyxocr.screenshot()
        dyxocr.save_img(img, 'err_find_daily_mainpage')
        return 1
    
    # 定位并进入多1赛事界面
    print('enter mp1 mainpage')
    nx.press_buttons(controller_index, [Buttons.ZR], down=0.2, up=0.5)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)

    return dyxocr.check_mp1_page()
    

# 多人1，比赛中用蓝喷保速
def mp1_race_DS(nx, controller_index):

    # 保存多1界面
    img = dyxocr.screenshot()
    img.save('current_mp1_page.jpg')

    # 进入并检查选车界面，若不对则返回错误 1
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=10)
    tag = dyxocr.check_mp1_carpage()
    if tag == 1:
        return 1

    # 选车 DS，若不对则返回错误 1
    nx.press_buttons(controller_index, [Buttons.ZL], down=0.2, up=1)
    nx.tilt_stick(controller_index, Sticks.LEFT_STICK, -100, 0, tilted=10, released=0.5)
    nx.press_buttons(controller_index, [Buttons.DPAD_RIGHT], down=0.2, up=0.5)
    nx.press_buttons(controller_index, [Buttons.DPAD_RIGHT], down=0.2, up=0.5)
    nx.press_buttons(controller_index, [Buttons.DPAD_RIGHT], down=0.2, up=1)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)

    tag, oil_tag = dyxocr.check_car('DS')
    if tag == 1:
        return 1

    # 开始比赛
    print('wait for start')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=1)
    time.sleep(30)

    print('start')
    for j in range(30):

        nx.press_buttons(controller_index, [Buttons.Y], down=0.2, up=0.5)
        nx.press_buttons(controller_index, [Buttons.Y], down=0.2, up=0.5)

        t1 = dyxocr.check_mp1_race()

        if t1 == 0:
            print(f'end loop {j}')
            break
        elif t1 == 1:
            print('err end race')
            img = dyxocr.screenshot()
            dyxocr.save_img(img, 'err_end_race')
            break

    if j == 29:
        print('err end full loop')
        img = dyxocr.screenshot()
        dyxocr.save_img(img, 'err_end_full_loop')

    # 结束比赛，退回到多1主界面
    print('end')
    for i in range(4):
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=5)
        nx.press_buttons(controller_index, [Buttons.B], down=0.2, up=1)
    
    # 进入多1界面
    print('enter mp1 mainpage')
    nx.press_buttons(controller_index, [Buttons.A], down=0.2, up=5)

    return dyxocr.check_mp1_page()



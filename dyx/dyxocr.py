"""
多人1+图像采集ocr监控
"""

import time
from PIL import Image, ImageFilter
import pytesseract
import os


# 保存图片，带时间戳
def save_img(img, name):

    t1 = time.localtime()
    t1 = time.strftime('%Y-%m-%d-%H-%M-%S', t1)
    pname = t1+'_'+name+'.jpg'
    img.save(pname)


# 截屏
def screenshot():
    
    while True:

        os.system('rm output.jpg')

        # 读取yuv图片
        cmd = r'v4l2-ctl --device /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=YUYV --stream-mmap --stream-to=./output.yuv --stream-count=1'

        os.system(cmd)
        time.sleep(1)
        os.system(cmd)
        time.sleep(1)

        # 读取jpg图片
        cmd = r'v4l2-ctl --device /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=MJPG --stream-mmap --stream-to=./output.jpg --stream-count=1'

        os.system(cmd)
        time.sleep(1)

        try:
            img = Image.open('output.jpg')
            break
        except:
            print('err load img')

    return img


# 识别多1主界面
def check_mp1_page():

    img_mp = screenshot()

    img = img_mp.crop((485,919,893,1015))
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'LEADERBOARD' in t:
        print('mp1 page check')
        return 0
    else:
        print('err check mp1 page')
        save_img(img_mp, 'err_check_mp1_page')
        return 1


# 识别选车界面
def check_mp1_carpage():

    img_car = screenshot()

    img = img_car.crop((136, 117, 693, 229))
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'SELECTION' in t:
        print('mp1 carpage check')
        return 0
    else:
        print('err check mp1 carpage')
        save_img(img_car, 'err_check_mp1_carpage')
        return 1


# 识别比赛界面
def check_mp1_race():

    img_race = screenshot()

    img = img_race.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'WIN' in t or 'NEXT' in t:
        return 0 # 检测到比赛结束，自动终止
    elif 'SERVER' in t or 'ERROR' in t:
        return 1 # 检测到连接错误，终止比赛
    else:
        return 2


# 识别车辆和剩余油量
def check_car(car):

    img_car = screenshot()

    # 识别车辆名称
    img = img_car.crop((100, 100, 600, 300))
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t1 = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    # 车辆识别失败，直接返回错误 1
    # 但油量不报错避免空耗时间
    if car in t1:
        print(f'check {car}')
    else:
        print(f'err check {car}')
        save_img(img_car, 'err_check_'+car)
        return 1, 2

    # 识别当前油量
    x = 713
    oil_tag = 0
    while x <=765:
        img = img_car.crop((x,963,907,1025))
        img = img.filter(ImageFilter.SHARPEN)
        img = img.convert('L')

        t2 = pytesseract.image_to_string(img, lang='eng', config='--psm 11')
        t2 = t2.split('/')
        if t2[0].isdigit():
            oil_tag = int(t2[0])
            break

        x = x + 5

    print(f'current oil {oil_tag}')

    return 0, oil_tag


# 检查ns主界面
def check_ns():

    img_ns = screenshot()

    img = img_ns.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'Asphalt' in t or 'Legends' in t:
        print('ns home check')
        return 0
    else:
        print('err check ns homepage')
        save_img(img_ns, 'err_check_ns_homepage')
        return 1


# 检查asphalt主界面
def check_asphalt():

    img_as = screenshot()

    img = img_as.crop((0, 950, 1920, 1000))
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'PASS' in t or 'PLAYER' in t or 'CAREER' in t:
        print('asphalt homepage check')
        return 0
    else:
        print('err check asphalt homepage')
        save_img(img_as, 'err_check_asphalt_homepage')
        return 1


# 检查每日赛事的主界面
def is_daily():

    img = screenshot()

    img=img.crop((500,880,710,1010))
    img=img.filter(ImageFilter.SHARPEN)
    img=img.convert('L')
    img = img.point( lambda p: 0 if p<10 else 255 )

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'DAILY' in t or 'EVENTS' in t:
        print('is daily mainpage')
        return 0
    else:
        print('not daily mainpage')
        return 1


# 检查寻车赛事的主界面
def is_car_hunt():

    img = screenshot()

    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert('L')
    img = img.point( lambda p: 255 if p > 200 else 0 )

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'CAR HUNT' in t and 'you will' in t:
        print('is car hunt page')
        return 0
    else:
        print('not car hunt page')
        return 1


# 检查寻车赛事主界面
def check_car_hunt_page():

    img_hunt = screenshot()

    img = img_hunt.filter(ImageFilter.SHARPEN)
    img = img.convert('L')
    img = img.point( lambda p: 255 if p > 200 else 0 )

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    if 'CAR HUNT' in t and 'you will' not in t:
        print('car hunt page check')
        return 0
    else:
        print('err check car hunt page')
        save_img(img_hunt,'err_check_car_hunt_page')
        return 1


# 识别寻车比赛界面
def check_car_hunt_race():

    img = screenshot()

    img = img.crop((360, 70, 990, 150))
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert('L')

    t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

    # 检测到比赛结束，自动终止
    if 'RACE' in t and 'RESULTS' in t:
        print('end race')
        return 0
    else:
        return 1


# 检查票数，出错则返回 0
def check_tickets():

    img_ticket = screenshot()

    x=1625
    ticket = 0
    while x < 1646:
        img = img_ticket.crop((x, 254, 1755, 302))
        img = img.filter(ImageFilter.SHARPEN)
        img = img.convert('L')

        t = pytesseract.image_to_string(img, lang='eng', config='--psm 11')

        t = t.split('/')

        if t[0].isdigit():
            ticket = int(t[0])
            break

        x = x + 10

    print(f'current ticket {ticket}')

    return ticket


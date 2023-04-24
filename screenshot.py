from subprocess import Popen, PIPE
from utils.log import logger


def screenshot():
    logger.info("Start screen shot")
    cmd = "v4l2-ctl --device /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=YUYV --stream-mmap --stream-to=./output.yuv --stream-count=1"
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd="./images")
    p.wait()
    cmd = "ffmpeg -loglevel quiet -y -s 1920*1080 -pix_fmt yuyv422 -i ./output.yuv ./output.jpg"
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd="./images")
    p.wait()
    logger.info("Finished screen shot")


if __name__ == "__main__":
    screenshot()
